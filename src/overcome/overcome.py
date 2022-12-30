"""
High performance approach to get the buying and selling earnings overcome.
"""

import numpy as np

from overcome.position.positions import Positions
from overcome.position.evaluation import Evaluation
from overcome.stack import Node, Stack

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

    def __init__(self, threshold, take_profit, stop_loss, positions_limit=-1):
        self.__threshold = threshold
        self.__tp = take_profit
        self.__sl = stop_loss
        self.__open_buying = Stack()
        self.__open_selling = Stack()
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
        self.__add_position = self.__choose_adding_method(positions_limit)

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
        earn_buying = np.zeros([len(high_low_close), 1], dtype=np.float32)
        earn_selling = np.zeros([len(high_low_close), 1], dtype=np.float32)
        values_iter = np.nditer(
            high_low_close,
            order='C',
            flags=['external_loop']
        )
        with values_iter:
            for index, [high, low, close] in enumerate(values_iter):
                self.__update_earnings(high, low, earn_buying, earn_selling)
                self.__add_position(index, close, self.__open_buying)
                self.__add_position(index, close, self.__open_selling)
        return earn_buying, earn_selling

    @staticmethod
    def __choose_adding_method(limit: int) -> callable:
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
            earn_selling: np.ndarray):
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
            self.__potential_loser
        )
        # Buying operation
        self.__update(
            high,
            low,
            earn_buying,
            self.__open_buying,
            self.__evaluation.evaluate_buying,
            self.__potential_winner
        )

    def __update(
            self,
            high: np.float32,
            low: np.float32,
            earnings: np.ndarray,
            open_positions: Stack,
            evaluate: callable,
            positions: Positions
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
        """
        self.__update_for_lose(
            high, low, earnings, open_positions, evaluate,
            positions.read_for_lose, positions.remove_for_lose)
        self.__update_for_win(
            high, low, earnings, open_positions, evaluate,
            positions.read_for_win, positions.remove_for_win)

    def __update_for_lose(
            self,
            high: np.float32,
            low: np.float32,
            earnings: np.ndarray,
            open_positions: Stack,
            evaluate: callable,
            read_for_lose: callable,
            remove_for_lose: callable
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
        if open_positions.empty():
            return
        node: Node = read_for_lose(open_positions)
        if Evaluation.LOSES == evaluate(node.priority, high, low):
            earnings[node.content] = self.__sl * (-1)
            remove_for_lose(open_positions)
            return self.__update_for_lose(
                high, low, earnings, open_positions, evaluate,
                read_for_lose, remove_for_lose
            )

    def __update_for_win(
            self,
            high: np.float32,
            low: np.float32,
            earnings: np.ndarray,
            open_positions: Stack,
            evaluate: callable,
            read_for_win: callable,
            remove_for_win: callable
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
        if open_positions.empty():
            return
        node: Node = read_for_win(open_positions)
        if Evaluation.WINS == evaluate(node.priority, high, low):
            earnings[node.content] = self.__tp
            remove_for_win(open_positions)
            return self.__update_for_win(
                high, low, earnings, open_positions, evaluate,
                read_for_win, remove_for_win
            )
