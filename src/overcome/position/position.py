import numpy as np

from src.overcome.position.evaluation import Evaluation


class Position:
    def __init__(
            self,
            index,
            value: np.float32,
            threshold: np.float32,
            wins_on_buying: callable,
            loses_on_buying: callable,
            wins_on_selling: callable,
            loses_on_selling: callable
    ):
        """
        Constructor.
        :param index: index within the dataframe. Any type
        :param value: the candles bar close value in this position
        :param threshold: precision threshold to compare the boundaries for
        winning, losing or doing nothing.
        :param wins_on_buying: function to check whether it wins on buying
        :param loses_on_buying: function to check whether it loses on buying
        :param wins_on_selling: function to check whether it wins on selling
        :param loses_on_selling: function to check whether it loses on selling
        """
        self.__index = index
        self.__value = value
        self.__threshold = threshold
        self.__wins_on_buying = wins_on_buying
        self.__loses_on_buying = loses_on_buying
        self.__wins_on_selling = wins_on_selling
        self.__loses_on_selling = loses_on_selling

    @property
    def index(self):
        return self.__index

    def evaluate_buying(
            self,
            low: np.float32,
            high: np.float32,
            take_profit: np.float32,
            stop_loss: np.float32
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
        if self.__wins_on_buying(high, take_profit, self.__value, self.__threshold):
            return Evaluation.WINS
        if self.__loses_on_buying(low, stop_loss, self.__value, self.__threshold):
            return Evaluation.LOSES
        return Evaluation.NONE

    def evaluate_selling(
            self,
            low: np.float32,
            high: np.float32,
            take_profit: np.float32,
            stop_loss: np.float32
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
        if self.__wins_on_selling(low, take_profit, self.__value, self.__threshold):
            return Evaluation.WINS
        if self.__loses_on_selling(high, stop_loss, self.__value, self.__threshold):
            return Evaluation.LOSES
        return Evaluation.NONE
