"""
Facade of the position package.
High performance approach to get the buying and selling earnings overcome.
"""
from dataclasses import dataclass

import numpy as np

from src.overcome.position.evaluation import Evaluation
from src.stack.stack import create, add, Node, empty, head, tail, pop, shift

POSITION_VALUE = 0
POSITION_INDEX = 1

THRESHOLD = np.float32(0.00001)

_stop_loss = 0.0
_take_profit = 0.0

_earn_buying = None
_earn_selling = None

_open_buying = tuple()
_open_selling = tuple()


@dataclass
class Edge:
    read_for_win: callable
    remove_for_win: callable
    read_for_lose: callable
    remove_for_lose: callable


def __initialize(high_low_close: np.ndarray, take_profit_, stop_loss_):
    global _take_profit, _stop_loss, \
        _earn_buying, _earn_selling, \
        _open_buying, _open_selling
    _take_profit = take_profit_
    _stop_loss = stop_loss_
    _earn_buying = np.zeros([len(high_low_close), 1], dtype=np.float32)
    _earn_selling = np.zeros([len(high_low_close), 1], dtype=np.float32)
    _open_buying = create()
    _open_selling = create()


def calculate_earnings(high_low_close: np.ndarray, take_profit_, stop_loss_):
    __initialize(high_low_close, take_profit_, stop_loss_)
    market_values_iterator = np.nditer(
        high_low_close,
        order='C',
        flags=['external_loop'])
    for index, row in enumerate(market_values_iterator):
        __set_earnings(
            row[0],
            row[1])
        __collect(index, row[2])
    return _earn_buying, _earn_selling


def __set_earnings(high, low):
    global _earn_buying, _earn_selling
    _earn_buying = __update(
        low,
        high,
        _earn_buying,
        _open_buying,
        __evaluate_buying,
        Edge(
            read_for_win=head,
            remove_for_win=shift,
            read_for_lose=tail,
            remove_for_lose=pop
        )
    )
    _earn_selling = __update(
        low,
        high,
        _earn_selling,
        _open_selling,
        __evaluate_selling,
        Edge(
            read_for_win=tail,
            remove_for_win=pop,
            read_for_lose=head,
            remove_for_lose=shift
        )
    )


def __collect(index, close):
    global _open_buying, _open_selling
    position: tuple = (close, index)
    add(_open_buying, position[POSITION_INDEX], position[POSITION_VALUE])
    add(_open_selling, position[POSITION_INDEX], position[POSITION_VALUE])


def __update_for_lose(
        low,
        high,
        data: np.ndarray,
        open_positions: tuple,
        evaluate: callable,
        edge: Edge):

    while not empty(open_positions):
        node: Node = edge.read_for_lose(open_positions)
        if Evaluation.LOSES == evaluate(node.priority, low, high):
            data[node.content] = _stop_loss * (-1)
        else:
            break
        edge.remove_for_lose(open_positions)


def __update_for_win(
        low,
        high,
        data: np.ndarray,
        open_positions: tuple,
        evaluate: callable,
        edge: Edge):
    while not empty(open_positions):
        node: Node = edge.read_for_win(open_positions)
        if Evaluation.WINS == evaluate(node.priority, low, high):
            data[node.content] = _take_profit
        else:
            break
        edge.remove_for_win(open_positions)


def __update(
        low,
        high,
        data: np.ndarray,
        open_positions: tuple,
        evaluate: callable,
        edge: Edge
):
    __update_for_win(low, high, data, open_positions, evaluate, edge)
    __update_for_lose(low, high, data, open_positions, evaluate, edge)

    return data


def __evaluate_buying(position_value, low, high):
    if __wins_on_buying(high, position_value):
        return Evaluation.WINS
    if __loses_on_buying(low, position_value):
        return Evaluation.LOSES
    return Evaluation.NONE


def __evaluate_selling(position_value, low, high):
    if __wins_on_selling(low, position_value):
        return Evaluation.WINS
    if __loses_on_selling(high, position_value):
        return Evaluation.LOSES
    return Evaluation.NONE


def __wins_on_buying(high: np.float32, value: np.float32):
    limit = value + _take_profit
    return np.isclose(high, limit, THRESHOLD) or high > limit


def __loses_on_buying(low: np.float32, value: np.float32):
    limit = value - _stop_loss
    return np.isclose(low, limit, THRESHOLD) or low < limit


def __wins_on_selling(low: np.float32, value: np.float32):
    limit = value - _take_profit
    return np.isclose(low, limit, THRESHOLD) or low < limit


def __loses_on_selling(high: np.float32, value: np.float32):
    limit = value + _stop_loss
    return np.isclose(high, limit, THRESHOLD) or high > limit
