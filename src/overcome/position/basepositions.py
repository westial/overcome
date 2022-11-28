from abc import ABC

from pandas import DataFrame

from src.overcome.position.evaluation import Evaluation
from src.overcome.position.position import Position
from src.overcome.position.positions import Positions


class BasePositions(Positions, ABC):
    _items = set()

    def insert(self, position: Position):
        self._items.add(position)

    @staticmethod
    def _update(
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            opened_positions: set,
            column,
            evaluate: callable):
        remaining_positions = set()
        while len(opened_positions):
            position: Position = opened_positions.pop()
            overcome = evaluate(position, low, high, take_profit, stop_loss)
            if Evaluation.WINS == overcome:
                df.loc[position.index, column] = take_profit
            elif Evaluation.LOSES == overcome:
                df.loc[position.index, column] = stop_loss * (-1)
            else:
                remaining_positions.add(position)
        return remaining_positions
