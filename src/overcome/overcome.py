import numpy as np
from pandas import DataFrame

from src.overcome.position import positionlib


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
            take_profit: np.float32,
            stop_loss: np.float32

    ):
        self.__tp = take_profit
        self.__sl = stop_loss
        self.__earn_buying = None
        self.__earn_selling = None

    def apply(self, to: DataFrame) -> DataFrame:
        """
        Traverse the input dataframe and add the columns "earn_buying",
        "earn_selling" with the earnings for every row according to the context
        take profit, stop loss and values in the row as close, high and low.

        First we convert the targeted columns into numpy arrays. We process the
        comparisons and changes over these arrays in an improved service,
        and then we merge them into the original dataframe as new columns.

        :param to: input dataframe
        :return: the new columns in addition to the input dataframe
        """
        self.__earn_buying = np.zeros([len(to), 1], dtype=np.float32)
        self.__earn_selling = np.zeros([len(to), 1], dtype=np.float32)
        high_low_close = to[["high", "low", "close"]].to_numpy(dtype=np.float32)
        (to["earn_buying"], to["earn_selling"]) = \
            positionlib.calculate_earnings(
                high_low_close,
                self.__tp,
                self.__sl)
        return to

