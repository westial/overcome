from pandas import DataFrame

from src.overcome.position.evaluation import Evaluation
from src.overcome.position.position import Position
from src.overcome.position.positions import Positions


class BasicPositions(Positions):
    def update_buying(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            opened_positions: set,
            column):
        return self.__update(
            low,
            high,
            take_profit,
            stop_loss,
            df,
            opened_positions,
            column,
            self.__evaluate_buying)

    def update_selling(
            self,
            low,
            high,
            take_profit,
            stop_loss,
            df: DataFrame,
            opened_positions: set,
            column):
        return self.__update(
            low,
            high,
            take_profit,
            stop_loss,
            df,
            opened_positions,
            column,
            self.__evaluate_selling)

    @staticmethod
    def __update(
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

    @staticmethod
    def __evaluate_buying(position, low, high, tp, sl):
        return position.evaluate_buying(low, high, tp, sl)

    @staticmethod
    def __evaluate_selling(position, low, high, tp, sl):
        return position.evaluate_selling(low, high, tp, sl)
