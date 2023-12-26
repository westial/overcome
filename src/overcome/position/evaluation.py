import numpy as np


class Evaluation:
    """
    This class represents an evaluation of a trading position
    """
    WINS = 1
    NONE = 0
    LOSES = -1

    def __init__(self, threshold, tp, sl):
        self.__threshold = threshold
        self.__tp = tp
        self.__sl = sl

    def evaluate_buying(self, position_value, high, low):
        """
        Evaluates the buying position based on the position value, high value, and low value.

        :param position_value: The value of the position.
        :param high: The highest value for the position.
        :param low: The lowest value for the position.
        :return: The evaluation of the buying position (LOSES, WINS, or NONE).
        """
        if self.__loses_on_buying(low, position_value):
            return Evaluation.LOSES
        if self.__wins_on_buying(high, position_value):
            return Evaluation.WINS
        return Evaluation.NONE

    def evaluate_selling(self, position_value, high, low):
        """
        Evaluate selling based on the position value, high and low prices.

        :param position_value: The value of the position.
        :param high: The highest price.
        :param low: The lowest price.

        :return: The evaluation result of the selling, which can be Evaluation.LOSES, Evaluation.WINS, or Evaluation.NONE.
        """
        if self.__loses_on_selling(high, position_value):
            return Evaluation.LOSES
        if self.__wins_on_selling(low, position_value):
            return Evaluation.WINS
        return Evaluation.NONE

    def __wins_on_buying(self, high: np.float32, value: np.float32):
        """
        Determines if buying at a given high price will result winning.

        :param high: The highest value in a given range.
        :param value: The value to be compared with the highest value.
        :return: True if the highest value is close to the limit (value + self.tp) or greater than the limit, False otherwise.
        """
        limit = value + self.__tp
        return np.isclose(high, limit, self.__threshold) or high > limit

    def __loses_on_buying(self, low: np.float32, value: np.float32):
        """
        Determines if buying at a given low price will result in a loss.

        :param low: The low price at which the buying will occur.
        :param value: The value that needs to be compared with the low price.
        :return: True if buying at the low price will result in a loss, False otherwise.
        """
        limit = value - self.__sl
        return np.isclose(low, limit, self.__threshold) or low < limit

    def __wins_on_selling(self, low: np.float32, value: np.float32):
        """
        Determines whether the selling price is within the acceptable range for winning.

        :param low: The lowest possible selling price.
        :param value: The selling price.
        :return: True if the selling price is within the acceptable range for winning, False otherwise.
        """
        limit = value - self.__tp
        return np.isclose(low, limit, self.__threshold) or low < limit

    def __loses_on_selling(self, high: np.float32, value: np.float32):
        """Check if the high value is close to the limit or greater than the limit.

        :param high: The high value.
        :param value: The value.
        :return: True if the high value is close to the limit or greater than the limit, False otherwise.
        """
        limit = value + self.__sl
        return np.isclose(high, limit, self.__threshold) or high > limit
