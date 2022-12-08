"""
Facade of the position package.
High performance approach to get the buying and selling earnings overcome.
"""

import numpy as np

from src.overcome.position.positions import Positions
from src.overcome.position.evaluation import Evaluation
from src.stack.stack import create, add, Node, empty, head, tail, pop, shift

POSITION_VALUE = 0
POSITION_INDEX = 1


class Overcome:
    """
    This service calculates the bid/ask outcome of every row in an input
    with the columns high, low and close values from stock exchange candle bars
    historical data.

    The input is expected to contain an already sorted historical results of
    a product of the stocks exchange market.

    Applying the overcome simulates to open a position on buying and a position
    on selling on every row in the input. Then it follows up all rows
    in the timeline, and it attempts to close every simulated position based on
    the stop loss and take profit predefined values.

    If the evaluation finds out that the row reaches the take profit then one of
    the new columns will keep exactly the take profit value. Otherwise, if the
    row reaches the stop loss the column will keep the stop loss value.

    The result tuple are an array with the buying and one for the selling
    earnings on every row.

    The precision used overall project is np.float32.
    """
    def __init__(self, threshold, take_profit, stop_loss):
        self.__threshold = threshold
        self.__tp = take_profit
        self.__sl = stop_loss
        self.__open_buying = create()
        self.__open_selling = create()
        self.__evaluation = Evaluation(threshold, take_profit, stop_loss)
        self.__potential_winner = Positions(
            read_for_win=head,
            remove_for_win=shift,
            read_for_lose=tail,
            remove_for_lose=pop
        )
        self.__potential_loser = Positions(
            read_for_win=tail,
            remove_for_win=pop,
            read_for_lose=head,
            remove_for_lose=shift
        )

    def apply(self, high_low_close: np.ndarray):
        """
        Given a numpy array with a shape of (1, 3), with subarray for high,
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
                add(self.__open_buying, index, close)
                add(self.__open_selling, index, close)
        return earn_buying, earn_selling

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
            open_positions: tuple,
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
            open_positions: tuple,
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
        if empty(open_positions):
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
            open_positions: tuple,
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
        if empty(open_positions):
            return
        node: Node = read_for_win(open_positions)
        if Evaluation.WINS == evaluate(node.priority, high, low):
            earnings[node.content] = self.__tp
            remove_for_win(open_positions)
            return self.__update_for_win(
                high, low, earnings, open_positions, evaluate,
                read_for_win, remove_for_win
            )
