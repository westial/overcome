from abc import ABC

import numpy as np
from pandas import DataFrame

from src.overcome.position.evaluation import Evaluation
from src.overcome.position.position import Position
from src.overcome.position.positions import Positions


class BasePositions(Positions, ABC):
    _items = set()

    def insert(self, position: Position):
        self._items.add(position)

    def _update(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            open_positions: set,
            column,
            evaluate: callable):
        remaining_positions = set()
        while len(open_positions):
            position: Position = open_positions.pop()
            overcome = evaluate(position, low, high, take_profit, stop_loss)
            if Evaluation.WINS == overcome:
                df.loc[position.index, column] = take_profit
            elif Evaluation.LOSES == overcome:
                df.loc[position.index, column] = stop_loss * (-1)
            else:
                remaining_positions.add(position)
        self._items = remaining_positions
        return df

    def _X_update(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            data: np.ndarray,
            open_positions: set,
            evaluate: callable):
        remaining_positions = set()
        while len(open_positions):
            position: Position = open_positions.pop()
            overcome = evaluate(position, low, high, take_profit, stop_loss)
            if Evaluation.WINS == overcome:
                data[position.index] = take_profit
            elif Evaluation.LOSES == overcome:
                data[position.index] = stop_loss * (-1)
            else:
                remaining_positions.add(position)
        self._items = remaining_positions
        return data
