import numpy as np

from src.overcome.cposition.cposition import CPosition
from src.overcome.position.factory import Factory


def _wins_on_buying(high: np.float32, take_profit: np.float32,
                     value: np.float32, threshold: np.float32):
    limit = value + take_profit
    return np.isclose(high, limit, threshold) or high > limit


def _loses_on_buying(low: np.float32, stop_loss: np.float32, value: np.float32, threshold: np.float32):
    limit = value - stop_loss
    return np.isclose(low, limit, threshold) or low < limit


def _wins_on_selling(low: np.float32, take_profit: np.float32, value: np.float32, threshold: np.float32):
    limit = value - take_profit
    return np.isclose(low, limit, threshold) or low < limit


def _loses_on_selling(high: np.float32, stop_loss: np.float32, value: np.float32, threshold: np.float32):
    limit = value + stop_loss
    return np.isclose(high, limit, threshold) or high > limit


class CPreciseFactory(Factory):
    def __init__(self, precision_threshold: np.float32):
        self.__threshold = precision_threshold

    def create(self, index, value: np.float32):
        return CPosition(
            index,
            value,
            self.__threshold,
            _wins_on_buying,
            _loses_on_buying,
            _wins_on_selling,
            _wins_on_buying
        )
