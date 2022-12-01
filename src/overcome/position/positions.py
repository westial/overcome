from abc import ABC, abstractmethod

import numpy as np

from src.overcome.position.position import Position


class Positions(ABC):
    @abstractmethod
    def update(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            data: np.ndarray):
        """
        Compare the open positions with the market state values and margins
        configuration and place the changes into the input indexed data. Then
        return this data.
        :param low: Market's current state for low
        :param high: Market's current state for high
        :param take_profit: Margin configuration on taking profit
        :param stop_loss: Margin configuration on stopping loss
        :param data: input data. A numpy array.
        :return: Potentially altered dataframe
        """
        pass

    @abstractmethod
    def insert(self, position: Position):
        pass

