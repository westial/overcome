from operator import itemgetter

import numpy as np
import pandas as pd

from overcome.calculator.outcomeprofits import OutcomeProfits
from overcome.overcome import Overcome
from overcome.position.evaluation import Evaluation
from overcome.stack.stack import Stack, Node


class Analysis:
    def __init__(
            self,
            position_threshold: np.float32,
            take_profit: np.float32,
            stop_loss: np.float32,
            categories: dict
    ):
        self.__threshold = position_threshold
        self.__tp = take_profit
        self.__sl = stop_loss
        self.__relax_category, self.__sell_category, self.__buy_category = (
            itemgetter("relax", "sell", "buy")(categories)
        )
        self.__outcome_profits = OutcomeProfits(
            buy_category=self.__buy_category,
            sell_category=self.__sell_category
        )
        self.__open_buying = Stack()
        self.__open_selling = Stack()
        self.__overlapped_buying = {}
        self.__overlapped_selling = {}
        self.__overlapped_buying_counter = 0
        self.__overlapped_selling_counter = 0
        self.__evaluation = Evaluation(position_threshold, take_profit, stop_loss)
        self.__earn_buying = {}

    def apply(self, predicted: pd.Series, ohlcv: pd.DataFrame):
        data = ohlcv.copy(deep=True)
        overcome = Overcome(self.__threshold, self.__tp, self.__sl)
        (data["earn_buying"], data["earn_selling"]) = overcome.apply(
            ohlcv[["high", "low", "close"]].to_numpy(dtype=np.float32)
        )
        missing_index = predicted.index.difference(data.index)
        same_index_data = data[~data.index.isin(missing_index)]
        same_index_data["operation"] = predicted
        same_index_data["overlapped_buying"] = 1
        return {
            "profits": self.__outcome_profits.calculate(same_index_data),
            "overlapped_buying": same_index_data["overlapped_buying"]
        }

    def X_apply(self, predicted: pd.Series, ohlcv: pd.DataFrame):
        missing_index = predicted.index.difference(ohlcv.index)
        data = ohlcv[~ohlcv.index.isin(missing_index)]
        data["operation"] = predicted
        values_iter = np.nditer(
            data[["high", "low", "close", "operation"]],
            order='C',
            flags=['external_loop']
        )
        with values_iter:
            # OHLCV's closing value maps to price as value for a new position
            for index, [high, low, price, operation] in enumerate(values_iter):
                self.__set_overlapped_buying_at(index)
                self.__close_buying_positions_with(high, low, index)
                self.__add_position_for(operation, index, price)
        return {
            "profits": pd.Series(self.__earn_buying, index=data.index).fillna(0),
            "overlapped_buying": pd.Series(self.__overlapped_buying, index=data.index).fillna(0)
        }

    def __set_overlapped_buying_at(self, index):
        self.__overlapped_buying[index] = self.__overlapped_buying_counter

    def __add_position_for(self, operation: int, index, value):
        """
        Adds a position for the specified operation, index, and value.

        :param operation: The operation category (either __buy_category or __sell_category).
        :param index: The index at which to add the position.
        :param value: The value of the position being added.
        :return: None
        """
        if self.__buy_category == operation:
            self.__open_buying.add(index, value)
            self.__increase_overlapped_buying()
            self.__set_overlapped_buying_at(index)
        elif self.__sell_category == operation:
            self.__open_selling.add(index, value)
            self.__increase_overlapped_selling()
            self.__set_overlapped_buying_at(index)

    def __increase_overlapped_buying(self):
        self.__overlapped_buying_counter += 1

    def __increase_overlapped_selling(self):
        self.__overlapped_selling_counter += 1

    def __evaluate_buying_to_win(self, high: np.float32, low: np.float32, index):
        if self.__open_buying.empty():
            return
        node: Node = self.__open_buying.head()
        node_index = node.content
        result = self.__evaluation.evaluate_buying(node.priority, high, low)
        if Evaluation.WINS == result:
            self.__open_buying.shift()
            self.__earn_buying[node_index] = self.__tp
            self.__decrease_overlapped_buying()
            return self.__evaluate_buying_to_win(high, low, index)

    def __evaluate_buying_to_lose(self, high: np.float32, low: np.float32, index):
        if self.__open_buying.empty():
            return
        node: Node = self.__open_buying.tail()
        node_index = node.content
        result = self.__evaluation.evaluate_buying(node.priority, high, low)
        if Evaluation.LOSES == result:
            self.__open_buying.pop()
            self.__earn_buying[node_index] = -self.__sl
            self.__decrease_overlapped_buying()
            return self.__evaluate_buying_to_lose(high, low, index)

    def __close_buying_positions_with(self, high: np.float32, low: np.float32, index):
        if not self.__open_buying.empty():
            self.__evaluate_buying_to_win(high, low, index)
        if not self.__open_buying.empty():
            self.__evaluate_buying_to_lose(high, low, index)

    def __decrease_overlapped_buying(self):
        self.__overlapped_buying_counter -= 1


