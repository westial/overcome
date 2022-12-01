import numpy as np
from pandas import DataFrame, Series

from src.overcome.position.positions import Positions
from src.overcome.position.factory import Factory
from src.overcome.position.position import Position


class Overcome:
    """
    This service calculates the bid/ask outcome of every row in an input
    dataframe with stock exchange candle bars data.

    The input dataframe is expected to contain a history of the results of a
    product of the stocks exchange market with at least the values open, high,
    and low. And the rows in the input dataframe must be sorted by time.

    Applying the overcome simulates to open a position on buying and a position
    on selling on every row in the input dataframe. Then it follows up all rows
    in the timeline, and it attempts to close every simulated position based on
    the stop loss and take profit predefined values.

    If the evaluation finds out that the row reaches the take profit then one of
    the new columns will keep exactly the take profit value. Otherwise, if the
    row reaches the stop loss the column will keep the stop loss value.

    The new columns are two, one for buying earnings and one for selling
    earnings. So, depending on the simulated operation, the overcome can be kept
    in one or another. One for every open position in every row.
    """
    def __init__(
            self,
            position_factory: Factory,
            take_profit: np.float32,
            stop_loss: np.float32,
            buying: Positions,
            selling: Positions

    ):
        self.__buying = buying
        self.__selling = selling
        self.__position_factory = position_factory
        self.__tp = take_profit
        self.__sl = stop_loss
        self.__earn_buying = None
        self.__earn_selling = None

    def apply(self, to: DataFrame) -> DataFrame:
        """
        Traverse the input dataframe and add the columns "earn_buying",
        "earn_selling" with the earnings for every row according to the context
        take profit, stop loss and values in the row as close, high and low.

        The index to map the rows in both, the earning updates and in the
        positions collection is a default incremental numeric range. That makes
        the data package simpler and numpy may be used instead of the original
        heavy dataframe.

        First we create the new columns as simple numpy arrays. We process the
        comparisons and changes over these arrays, and then we merge them into
        the original dataframe as new columns.

        :param to: input dataframe
        :return: the new columns in addition to the input dataframe
        """
        self.__earn_buying = np.zeros([len(to), 1], dtype=np.float32)
        self.__earn_selling = np.zeros([len(to), 1], dtype=np.float32)
        for index, row in enumerate(to[["high", "low", "close"]].itertuples(index=False)):
            self.__set_earnings(row[0], row[1])
            self.__collect(index, row[2])
        to["earn_buying"] = self.__earn_buying
        to["earn_selling"] = self.__earn_selling
        return to

    def __collect(self, index, close):
        position: Position = self.__position_factory.create(index, close)
        self.__buying.insert(position)
        self.__selling.insert(position)

    def __set_earnings(self, high, low):
        self.__earn_buying = self.__buying.update(
            low, high, self.__tp, self.__sl, self.__earn_buying)
        self.__earn_selling = self.__selling.update(
            low, high, self.__tp, self.__sl, self.__earn_selling)
