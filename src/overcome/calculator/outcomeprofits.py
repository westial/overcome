import numpy as np
from pandas import DataFrame


class OutcomeProfits:
    """
    Calculate the outcome profits from a predicted data segment by comparing the
    predicted column "operation" with the pre overcome columns "earn_buying" and
    "earn_selling".
    """
    def __init__(self, sell_category: int, buy_category: int):
        self.__df = None
        self.__sell_category = sell_category
        self.__buy_category = buy_category

    def calculate(self, data: DataFrame) -> DataFrame:
        """
        Calculate the profits for each row in the given data

        :param data: prediction output data after got passed through {@link Overcome}.
        Columns "operation", "earn_buying", "earn_selling" are mandatory.
        """
        if None is data:
            raise ValueError("Empty data")
        data["profits"] = np.float32(0)
        data.loc[data["operation"] == self.__buy_category, "profits"] = \
            data["earn_buying"]
        data.loc[data["operation"] == self.__sell_category, "profits"] = \
            data["earn_selling"]
        return data["profits"]
