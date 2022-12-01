import numpy as np

from src.overcome.position.factory import Factory
from src.overcome.position.position import Position


class PreciseFactory(Factory):
    def __init__(self, precision_threshold: float):
        self.__threshold = precision_threshold

    def create(self, index, value: np.float32):
        return Position(index, value, self.__threshold)
