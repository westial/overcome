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
            opened_positions: set,
            column):
        return self._update(
            low,
            high,
            take_profit,
            stop_loss,
            df,
            opened_positions,
            column,
            self.__evaluate_selling)

    @staticmethod
    def __evaluate_selling(position, low, high, tp, sl):
        return position.evaluate_selling(low, high, tp, sl)
