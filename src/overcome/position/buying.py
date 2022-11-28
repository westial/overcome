from pandas import DataFrame

from src.overcome.position.basepositions import BasePositions


class Buying(BasePositions):
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
            self.__evaluate_buying)

    @staticmethod
    def __evaluate_buying(position, low, high, tp, sl):
        return position.evaluate_buying(low, high, tp, sl)
