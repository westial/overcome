from operator import itemgetter

import numpy as np
import pandas as pd

from overcome.position.evaluation import Evaluation
from overcome.stack.stack import Stack, Node


class Analysis:
    def __init__(
            self,
            threshold: np.float32,
            take_profit: np.float32,
            stop_loss: np.float32,
            categories: dict[str: int, str: int, str: int]
    ):
        """
        This method initializes the instance variables of the class. It takes in the threshold, take_profit,
        stop_loss, and categories parameters and assigns them to the corresponding instance variables. It also creates
        other required instance variables such as stacks for buying and selling, dictionaries for overlapped buying
        and selling, counters for overlapped buying and selling, an Evaluation object, and dictionaries for earnings
        from buying and selling.

        :param threshold: The threshold value to consider for buying or selling a stock. Must be a float.
        :param take_profit: The take profit value for a stock. Must be a float.
        :param stop_loss: The stop loss value for a stock. Must be a float.
        :param categories: A dictionary containing the "relax", "sell", and "buy" categories for the stock,
        exactly with that keys "relax", "sell", and "buy" and an integer as value.
        """
        self.__threshold = threshold
        self.__tp = take_profit
        self.__sl = stop_loss
        self.__relax_category, self.__sell_category, self.__buy_category = (
            itemgetter("relax", "sell", "buy")(categories)
        )
        self.__open_buying = Stack()
        self.__open_selling = Stack()
        self.__overlapped_buying = {}
        self.__overlapped_selling = {}
        self.__overlapped_buying_counter = 0
        self.__overlapped_selling_counter = 0
        self.__evaluation = Evaluation(
            threshold,
            take_profit,
            stop_loss
        )
        self.__earn_buying = {}
        self.__earn_selling = {}

    def apply(self, predicted: pd.Series, ohlcv: pd.DataFrame) -> dict:
        """
        Apply predicted values to the OHLCV data to calculate profits and
        overlapped positions.

        :param predicted: Predicted values of the operation.
        :param ohlcv: OHLCV data containing high, low, close values.
        :return: Dictionary containing calculated profits and overlapped
        positions. The returned dictionary keys are profits_buying,
        profits_selling, overlapped_buying, overlapped_selling.
        """
        missing_index = predicted.index.difference(ohlcv.index)
        data = ohlcv[~ohlcv.index.isin(missing_index)]
        data["operation"] = predicted
        for index, row in data.iterrows():
            self.__set_all_overlapped_at(index)
            self.__close_positions_with(row["high"], row["low"], index)
            self.__add_position_for(row["operation"], index, row["close"])
        return {
            "profits_buying": pd.Series(
                self.__earn_buying, index=data.index, dtype=np.float32
            ).fillna(0),
            "profits_selling": pd.Series(
                self.__earn_selling, index=data.index, dtype=np.float32
            ).fillna(0),
            "overlapped_buying": pd.Series(
                self.__overlapped_buying, index=data.index
            ),
            "overlapped_selling": pd.Series(
                self.__overlapped_selling, index=data.index
            )
        }

    def __set_all_overlapped_at(self, index):
        self.__set_overlapped_buying_at(index)
        self.__set_overlapped_selling_at(index)

    def __set_overlapped_buying_at(self, index):
        self.__overlapped_buying[index] = self.__overlapped_buying_counter

    def __set_overlapped_selling_at(self, index):
        self.__overlapped_selling[index] = self.__overlapped_selling_counter

    def __add_position_for(self, operation: int, index, value):
        """
        Adds a position for the specified operation, index, and value.

        :param operation: The operation category.
        :param index: The index at which to add the position.
        :param value: The value of the position being added.
        :return: None
        """
        if self.__buy_category == operation:
            self.__open_buying.add(index, value)
            self.__overlapped_buying_counter += 1
            self.__set_overlapped_buying_at(index)
        elif self.__sell_category == operation:
            self.__open_selling.add(index, value)
            self.__overlapped_selling_counter += 1
            self.__set_overlapped_selling_at(index)

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

    def __evaluate_selling_to_win(self, high: np.float32, low: np.float32, index):
        if self.__open_selling.empty():
            return
        node: Node = self.__open_selling.tail()
        node_index = node.content
        result = self.__evaluation.evaluate_selling(node.priority, high, low)
        if Evaluation.WINS == result:
            self.__open_selling.pop()
            self.__earn_selling[node_index] = self.__tp
            self.__decrease_overlapped_selling()
            return self.__evaluate_selling_to_win(high, low, index)

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

    def __evaluate_selling_to_lose(self, high: np.float32, low: np.float32, index):
        if self.__open_selling.empty():
            return
        node: Node = self.__open_selling.head()
        node_index = node.content
        result = self.__evaluation.evaluate_selling(node.priority, high, low)
        if Evaluation.LOSES == result:
            self.__open_selling.shift()
            self.__earn_selling[node_index] = -self.__sl
            self.__decrease_overlapped_selling()
            return self.__evaluate_selling_to_lose(high, low, index)

    def __close_positions_with(self, high: np.float32, low: np.float32, index):
        self.__close_buying_positions_with(high, low, index)
        self.__close_selling_positions_with(high, low, index)

    def __close_selling_positions_with(self, high: np.float32, low: np.float32, index):
        closing = [
            self.__evaluate_buying_to_win,
            self.__evaluate_buying_to_lose,
            self.__evaluate_selling_to_win,
            self.__evaluate_selling_to_lose
        ]
        while closing and not self.__open_selling.empty():
            closing.pop(0)(high, low, index)

    def __close_buying_positions_with(self, high: np.float32, low: np.float32, index):
        closing = [
            self.__evaluate_buying_to_win,
            self.__evaluate_buying_to_lose,
            self.__evaluate_selling_to_win,
            self.__evaluate_selling_to_lose
        ]
        while closing and not self.__open_buying.empty():
            closing.pop(0)(high, low, index)

    def __decrease_overlapped_buying(self):
        self.__overlapped_buying_counter -= 1

    def __decrease_overlapped_selling(self):
        self.__overlapped_selling_counter -= 1


