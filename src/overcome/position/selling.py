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
        self._items = self._update(
            low,
            high,
            take_profit,
            stop_loss,
            df,
            self._items,
            column,
            self.__evaluate_selling)

    @staticmethod
    def __evaluate_selling(position, low, high, tp, sl):
        return position.evaluate_selling(low, high, tp, sl)
