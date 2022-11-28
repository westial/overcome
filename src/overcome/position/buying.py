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
            self.__evaluate_buying)

    @staticmethod
    def __evaluate_buying(position, low, high, tp, sl):
        return position.evaluate_buying(low, high, tp, sl)
