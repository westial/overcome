import numpy as np


class Evaluation:
    WINS = 1
    NONE = 0
    LOSES = -1

    def __init__(self, threshold, tp, sl):
        self.__threshold = threshold
        self.__tp = tp
        self.__sl = sl

    def evaluate_buying(self, position_value, high, low):
        if self.__loses_on_buying(low, position_value):
            return Evaluation.LOSES
        if self.__wins_on_buying(high, position_value):
            return Evaluation.WINS
        return Evaluation.NONE

    def evaluate_selling(self, position_value, high, low):
        if self.__loses_on_selling(high, position_value):
            return Evaluation.LOSES
        if self.__wins_on_selling(low, position_value):
            return Evaluation.WINS
        return Evaluation.NONE

    def __wins_on_buying(self, high: np.float32, value: np.float32):
        limit = value + self.__tp
        return np.isclose(high, limit, self.__threshold) or high > limit

    def __loses_on_buying(self, low: np.float32, value: np.float32):
        limit = value - self.__sl
        return np.isclose(low, limit, self.__threshold) or low < limit

    def __wins_on_selling(self, low: np.float32, value: np.float32):
        limit = value - self.__tp
        return np.isclose(low, limit, self.__threshold) or low < limit

    def __loses_on_selling(self, high: np.float32, value: np.float32):
        limit = value + self.__sl
        return np.isclose(high, limit, self.__threshold) or high > limit
