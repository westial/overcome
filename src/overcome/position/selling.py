import numpy as np
from pandas import DataFrame

from src.overcome.position.basepositions import BasePositions


class Selling(BasePositions):
    def update(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            column):
        return self._update(
            low,
            high,
            take_profit,
            stop_loss,
            df,
            self._items,
            column,
            self.__evaluate_selling)

    def X_update(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            data: np.ndarray):
        return self._X_update(
            low,
            high,
            take_profit,
            stop_loss,
            data,
            self._items,
            self.__evaluate_selling)

    @staticmethod
    def __evaluate_selling(position, low, high, tp, sl):
        return position.evaluate_selling(low, high, tp, sl)
