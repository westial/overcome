from abc import ABC, abstractmethod

from pandas import DataFrame


class Positions(ABC):
    @abstractmethod
    def update_buying(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            opened_positions: set,
            column):
        pass

    @abstractmethod
    def update_selling(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            opened_positions: set,
            column):
        pass
