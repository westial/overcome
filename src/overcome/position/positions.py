from abc import ABC, abstractmethod

from pandas import DataFrame

from src.overcome.position.position import Position


class Positions(ABC):
    @abstractmethod
    def update(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            column):
        pass

    @abstractmethod
    def insert(self, position: Position):
        pass

