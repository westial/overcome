"""
High performance approach to get the buying and selling earnings overcome.
"""

import numpy as np
import pandas as pd

from overcome.position.positions import Positions
from overcome.position.evaluation import Evaluation
from overcome.stack.measuredstack import MeasuredStack
from overcome.stack.stack import Node, Stack

POSITION_VALUE = 0
POSITION_INDEX = 1


class Overcome:
    """
    Given a constant take profit and a stop loss, and a time base sorted data
    vector with the "high", "low", and "close" values from a stock market
    product, Overcome calculates the potential earnings in both, buying and
    selling for every step in the timeline.

    Optionally you can set a positions number limit. When there is
    already this number of opened positions, the following
    positions are not virtually opened. So, these following positions does not
    win or lose any amount of money. The limit is -1 by default, then there is
    no limit.

    The precision used overall project is np.float32.
    """

    def __init__(
            self,
            threshold,
            take_profit,
            stop_loss,
            positions_limit=-1,
            has_counters=False,
            max_delay=0
    ):
        """
        Maximum delay is the maximum number of rows between the position
        starting row and the position closing one. 0 by defaults means there is
        no maximum and the position may close wherever it does. That delay
        control keeps the expectation for fast outcomes only as the most
        reliable ones. It is set by the input seed.
        """
        self.__open_buying_lengths = pd.Series(dtype=np.int16)
        self.__open_selling_lengths = pd.Series(dtype=np.int16)
        self.__threshold = threshold
        self.__tp = take_profit
        self.__sl = stop_loss
        self.__set_counters(has_counters, max_delay)
        self.__open_buying = self.__create_buying_stack()
        self.__open_selling = self.__create_selling_stack()
        self.__evaluation = Evaluation(threshold, take_profit, stop_loss)
        self.__potential_winner = Positions(
            read_for_win=lambda s: s.head(),
            remove_for_win=lambda s: s.shift(),
            read_for_lose=lambda s: s.tail(),
            remove_for_lose=lambda s: s.pop()
        )
        self.__potential_loser = Positions(
            read_for_win=lambda s: s.tail(),
            remove_for_win=lambda s: s.pop(),
            read_for_lose=lambda s: s.head(),
            remove_for_lose=lambda s: s.shift()
        )
        self.__add_position = self.__create_adding(positions_limit)

    def __set_counters(self, has_counters, max_delay):
        """
        Set maximum delay and enable counters
        
        Force to enable counters when maximum delay is set
        """
        self.__max_delay = max_delay
        self.__has_counters = True if 0 < max_delay else has_counters

    def __create_buying_stack(self):
        if self.__has_counters:
            return self.__create_buying_measured_stack()
        return self.__create_simple_stack()

    def __create_selling_stack(self):
        if self.__has_counters:
            return self.__create_selling_measured_stack()
        return self.__create_simple_stack()

    @staticmethod
    def __create_simple_stack():
        return Stack()

    def __create_buying_measured_stack(self):
        return MeasuredStack(self.__open_buying_lengths)

    def __create_selling_measured_stack(self):
        return MeasuredStack(self.__open_selling_lengths)

    def apply(self, high_low_close: np.ndarray):
        """
        Given a numpy array with a shape of (length, 3), with subarray for high,
        low and close values from a historical stock exchange data set,
        calculates the overcome and returns a tuple with the values of
        the potential earnings for buying positions at left and for selling
        positions at right.

        Pandas Dataframe is not supported here due to keep the fewer
        dependencies as possible. To convert high, low and close columns from a
        Dataframe into the required input see the following example.

        ```
        high_low_close = df[["high", "low", "close"]].to_numpy(dtype=np.float32)
        ```
        
        Then the result may be merged into the original Dataframe as follows.

        ```
        (df["earn_buying"], df["earn_selling"]) = overcome.apply(high_low_close)
        ```
        :param high_low_close: np.ndarray with high, low and close values arrays
        :return: tuple of np.ndarray with the buying and selling earnings
        respectively
        """
        earn_buying = np.zeros([len(high_low_close), ], dtype=np.float32)
        earn_selling = np.zeros([len(high_low_close), ], dtype=np.float32)
        buying_lengths = pd.Series(dtype=np.int16)
        selling_lengths = pd.Series(dtype=np.int16)
        values_iter = np.nditer(
            high_low_close,
            order='C',
            flags=['external_loop']
        )
        with values_iter:
            for index, [high, low, close] in enumerate(values_iter):
                if np.isnan(close):
                    continue
                self.__update_earnings(
                    high,
                    low,
                    earn_buying,
                    earn_selling,
                    buying_lengths,
                    selling_lengths
                )
                self.__add_position(index, close, self.__open_buying)
                self.__add_position(index, close, self.__open_selling)
        if self.__has_counters:
            return self.__ignore_delayed_earnings(
                earn_buying,
                earn_selling,
                self.__normalize(buying_lengths, earn_buying),
                self.__normalize(selling_lengths, earn_selling)
            )
        return earn_buying, earn_selling

    def __ignore_delayed_earnings(
            self,
            earn_buying,
            earn_selling,
            buying_lengths,
            selling_lengths
    ):
        if self.__max_delay:
            delayed_buy_index = buying_lengths > self.__max_delay
            delayed_sell_index = selling_lengths > self.__max_delay
            earn_buying[delayed_buy_index] = 0.0
            earn_selling[delayed_sell_index] = 0.0
        return (
            earn_buying,
            earn_selling,
            buying_lengths,
            selling_lengths
        )

    @staticmethod
    def __normalize(values: pd.Series, according_to: np.ndarray) -> np.ndarray:
        """
        Take a Series instance, reindex according to the given array and return
        an array with the new index and the Series' values.
        """
        return values.reindex(
            list(range(0, len(according_to))),
            fill_value=0
        ).to_numpy()

    @staticmethod
    def __create_adding(limit: int) -> callable:
        def add_position_limited(index, value, to: Stack):
            if limit > len(to):
                to.add(index, value)

        def add_position_unlimited(index, value, to: Stack):
            to.add(index, value)

        if 0 > limit:
            return add_position_unlimited
        return add_position_limited

    def __update_earnings(
            self,
            high: np.float32,
            low: np.float32,
            earn_buying: np.ndarray,
            earn_selling: np.ndarray,
            buying_lengths: pd.Series,
            selling_lengths: pd.Series
    ):
        """
        Update earnings in-place, for buying and selling operations among
        every open position in each operation data vector
        :param high: current row's high value
        :param low: current row's low value
        :param earn_buying: data vector for buying operation
        :param earn_selling: data vector for selling operation
        """
        # Selling operation
        self.__update(
            high,
            low,
            earn_selling,
            self.__open_selling,
            self.__evaluation.evaluate_selling,
            self.__potential_loser,
            selling_lengths
        )
        # Buying operation
        self.__update(
            high,
            low,
            earn_buying,
            self.__open_buying,
            self.__evaluation.evaluate_buying,
            self.__potential_winner,
            buying_lengths
        )

    def __update(
            self,
            high: np.float32,
            low: np.float32,
            earnings: np.ndarray,
            open_positions: Stack,
            evaluate: callable,
            positions: Positions,
            lengths: pd.Series
    ):
        """
        Evaluate and update in-place the open positions in one only operation,
        buying or selling
        :param high: current row's high value
        :param low: current row's low value
        :param earnings: earnings vector for one operation
        :param open_positions: open positions about one operation
        :param evaluate: callback to evaluate whether the current row value wins
            or loses on one operation
        :param positions: helper functions to read and remove an open position
        from the given vector
        :param lengths: lengths vector for one operation
        """
        self.__update_for_lose(
            high, low, earnings, open_positions, evaluate,
            positions.read_for_lose, positions.remove_for_lose, lengths)
        self.__update_for_win(
            high, low, earnings, open_positions, evaluate,
            positions.read_for_win, positions.remove_for_win, lengths)

    def __update_for_lose(
            self,
            high: np.float32,
            low: np.float32,
            earnings: np.ndarray,
            positions: Stack,
            evaluate: callable,
            read_for_lose: callable,
            remove_for_lose: callable,
            lengths: pd.Series
    ):
        """
        This algorithm in combination with the @link src.stack.stack double
        linked queue makes the traversing among the open positions faster and
        lighter.

        The stack vector is sorted from lower to bigger or the opposite
        depending on the target of the evaluation: earnings for buying or
        selling together with the updating intent for losing or winning.

        So when it evaluates false it leaves the traversing because the
        following values will evaluate false indeed. If it evaluates true then
        it recursively evaluates the following until one evaluates false because
        the following may be equal of the one that evaluated true.
        """
        if positions.empty():
            return
        node: Node = read_for_lose(positions)
        if Evaluation.LOSES == evaluate(node.priority, high, low):
            earnings[node.content] = self.__sl * (-1)
            self.__copy_from(positions, lengths, node.content)
            remove_for_lose(positions)
            return self.__update_for_lose(
                high, low, earnings, positions, evaluate,
                read_for_lose, remove_for_lose, lengths
            )

    def __copy_from(self, positions: MeasuredStack, to_lengths: pd.Series,
                    at_index):
        if not positions.empty() and self.__has_counters:
            to_lengths.loc[at_index] = positions.length_of(at_index) + 1

    def __update_for_win(
            self,
            high: np.float32,
            low: np.float32,
            earnings: np.ndarray,
            positions: Stack,
            evaluate: callable,
            read_for_win: callable,
            remove_for_win: callable,
            lengths: pd.Series
    ):
        """
        This algorithm in combination with the @link src.stack.stack double
        linked queue makes the traversing among the open positions faster and
        lighter.

        The stack vector is sorted from lower to bigger or the opposite
        depending on the target of the evaluation: earnings for buying or
        selling together with the updating intent for losing or winning.

        So when it evaluates false it leaves the traversing because the
        following values will evaluate false indeed. If it evaluates true then
        it recursively evaluates the following until one evaluates false because
        the following may be equal of the one that evaluated true.
        """
        if positions.empty():
            return
        node: Node = read_for_win(positions)
        if Evaluation.WINS == evaluate(node.priority, high, low):
            earnings[node.content] = self.__tp
            self.__copy_from(positions, lengths, node.content)
            remove_for_win(positions)
            return self.__update_for_win(
                high, low, earnings, positions, evaluate,
                read_for_win, remove_for_win, lengths
            )
