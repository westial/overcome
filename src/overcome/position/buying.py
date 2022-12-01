import numpy as np

from src.overcome.position.basepositions import BasePositions


class Buying(BasePositions):
    def update(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            data: np.ndarray):
        return self._update(
            low,
            high,
            take_profit,
            stop_loss,
            data,
            self._items,
            self.__evaluate_buying)

    @staticmethod
    def __evaluate_buying(position, low, high, tp, sl):
        return position.evaluate_buying(low, high, tp, sl)
