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
    in one or another. One for every opened position in every row.
    """
    def __init__(
            self,
            position_factory: Factory,
            take_profit: np.float64,
            stop_loss: np.float64,
            buying: Positions,
            selling: Positions

    ):
        self.__buying = buying
        self.__selling = selling
        self.__position_factory = position_factory
        self.__tp = take_profit
        self.__sl = stop_loss

    def apply(self, to: DataFrame) -> DataFrame:
        """
        Traverse the input dataframe and add the columns "earn_buying",
        "earn_selling" with the earnings for every row according to the context
        take profit, stop loss and values in the row as close, high and low.
        :param to: input dataframe
        :return: the new columns in addition to the input dataframe
        """
        to.loc[:, ["earn_buying", "earn_selling"]] = 0
        for index, row in to.iterrows():
            to = self.__set_earnings(to, row)
            self.__collect(index, row)
        return to

    def __collect(self, index, values: Series):
        """
        Create a new opened position and keep it in opened position repositories
        :param index: dataframe index value
        :param values: dataframe row
        """
        value = values["close"]
        position: Position = self.__position_factory.create(index, value)
        self.__buying.insert(position)
        self.__selling.insert(position)

    def __set_earnings(self, into: DataFrame, with_values: Series):
        """
        Calculate earnings comparing the new input values and the opened
        positions values in both sides, buying and selling. Then set the
        earnings value into the dataframe and returns the dataframe.
        :param into: dataframe to set the value in
        :param with_values: values to compare opened positions with
        :return the updated dataframe
        """
        high = with_values["high"]
        low = with_values["low"]
        into = self.__buying.update(
            low, high, self.__tp, self.__sl, into, "earn_buying")
        into = self.__selling.update(
            low, high, self.__tp, self.__sl, into, "earn_selling")
        return into
