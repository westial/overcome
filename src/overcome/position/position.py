import numpy as np

from src.overcome.position.evaluation import Evaluation


class Position:
    def __init__(self, index, value: np.float64, threshold: float):
        """
        Constructor.
        :param index: index within the dataframe. Any type
        :param value: the candles bar close value in this position
        :param threshold: precision threshold to compare the boundaries for
        winning, losing or doing nothing.
        """
        self.__index = index
        self.__value = value
        self.__threshold = threshold

    @property
    def index(self):
        return self.__index

    def evaluate_buying(
            self,
            low: np.float64,
            high: np.float64,
            take_profit: np.float64,
            stop_loss: np.float64
    ) -> Evaluation:
        """
        Evaluate whether the position closes on buying operation.
        :param low: candle bars low value
        :param high: candle bars high value
        :param take_profit: value set as profit boundary
        :param stop_loss:  value set as loss boundary
        :return: Return an Evaluation value describing whether buying loses or
        wins.
        """
        if self.__wins_on_buying(high, take_profit):
            return Evaluation.WINS
        if self.__loses_on_buying(low, stop_loss):
            return Evaluation.LOSES
        return Evaluation.NONE

    def evaluate_selling(
            self,
            low: np.float64,
            high: np.float64,
            take_profit: np.float64,
            stop_loss: np.float64
    ) -> Evaluation:
        """
        Evaluate whether the position closes on selling operation.
        :param low: candle bars low value
        :param high: candle bars high value
        :param take_profit: value set as profit boundary
        :param stop_loss:  value set as loss boundary
        :return: Return an Evaluation value describing whether selling loses or
        wins.
        """
        if self.__wins_on_selling(low, take_profit):
            return Evaluation.WINS
        if self.__loses_on_selling(high, stop_loss):
            return Evaluation.LOSES
        return Evaluation.NONE

    def __wins_on_buying(self, high: np.float64, take_profit: np.float64):
        limit = self.__value + take_profit
        return np.isclose(high, limit, self.__threshold) or high > limit

    def __loses_on_buying(self, low: np.float64, stop_loss: np.float64):
        limit = self.__value - stop_loss
        return np.isclose(low, limit, self.__threshold) or low < limit

    def __wins_on_selling(self, low: np.float64, take_profit: np.float64):
        limit = self.__value - take_profit
        return np.isclose(low, limit, self.__threshold) or low < limit

    def __loses_on_selling(self, high: np.float64, stop_loss: np.float64):
        limit = self.__value + stop_loss
        return np.isclose(high, limit, self.__threshold) or high > limit
