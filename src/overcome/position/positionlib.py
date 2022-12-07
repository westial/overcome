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

_stop_loss = 0.0
_take_profit = 0.0
_threshold = 0.0

_earn_buying = np.ndarray([])
_earn_selling = np.ndarray([])

_open_buying = tuple()
_open_selling = tuple()


@dataclass
class Edge:
    read_for_win: callable
    remove_for_win: callable
    read_for_lose: callable
    remove_for_lose: callable


def __initialize(
        high_low_close: np.ndarray,
        take_profit_,
        stop_loss_,
        threshold_):
    global _take_profit, _stop_loss, _threshold, \
        _earn_buying, _earn_selling, \
        _open_buying, _open_selling
    _take_profit = take_profit_
    _stop_loss = stop_loss_
    _threshold = threshold_
    _earn_buying = np.zeros([len(high_low_close), 1], dtype=np.float32)
    _earn_selling = np.zeros([len(high_low_close), 1], dtype=np.float32)
    _open_buying = create()
    _open_selling = create()


def calculate_earnings(
        high_low_close: np.ndarray,
        take_profit_,
        stop_loss_,
        threshold_
):
    global _open_buying, _open_selling, _earn_buying, _earn_selling
    __initialize(high_low_close, take_profit_, stop_loss_, threshold_)
    market_values_iterator = np.nditer(high_low_close, order='C', flags=['external_loop'])
    winner_edge = Edge(
            read_for_win=head,
            remove_for_win=shift,
            read_for_lose=tail,
            remove_for_lose=pop
        )
    loser_edge = Edge(
            read_for_win=tail,
            remove_for_win=pop,
            read_for_lose=head,
            remove_for_lose=shift
        )
    with market_values_iterator:
        for index, [high, low, close] in enumerate(market_values_iterator):
            __set_earnings(high, low, winner_edge, loser_edge)
            add(_open_buying, index, close)
            add(_open_selling, index, close)
    return _earn_buying, _earn_selling


def __set_earnings(high, low, winner_edge: Edge, loser_edge: Edge):
    global _earn_buying, _earn_selling, _open_buying, _open_selling
    __update(
        low,
        high,
        _earn_buying,
        _open_buying,
        __evaluate_buying,
        winner_edge
    )
    __update(
        low,
        high,
        _earn_selling,
        _open_selling,
        __evaluate_selling,
        loser_edge
    )


def __update_for_lose(
        low,
        high,
        data: np.ndarray,
        open_positions: tuple,
        evaluate: callable,
        read_for_lose: callable,
        remove_for_lose: callable
):
    if empty(open_positions):
        return
    node: Node = read_for_lose(open_positions)
    if Evaluation.LOSES == evaluate(node.priority, low, high):
        data[node.content] = _stop_loss * (-1)
        remove_for_lose(open_positions)
        return __update_for_lose(
            low, high, data, open_positions, evaluate,
            read_for_lose, remove_for_lose
        )


def __update_for_win(
        low,
        high,
        data: np.ndarray,
        open_positions: tuple,
        evaluate: callable,
        read_for_win: callable,
        remove_for_win: callable
):
    if empty(open_positions):
        return
    node: Node = read_for_win(open_positions)
    if Evaluation.WINS == evaluate(node.priority, low, high):
        data[node.content] = _take_profit
        remove_for_win(open_positions)
        return __update_for_win(
            low, high, data, open_positions, evaluate,
            read_for_win, remove_for_win
        )


def __update(
        low,
        high,
        data: np.ndarray,
        open_positions: tuple,
        evaluate: callable,
        edge: Edge
):
    __update_for_lose(
        low, high, data, open_positions, evaluate,
        edge.read_for_lose, edge.remove_for_lose)
    __update_for_win(
        low, high, data, open_positions, evaluate,
        edge.read_for_win, edge.remove_for_win)


def __evaluate_buying(position_value, low, high):
    if __loses_on_buying(low, position_value):
        return Evaluation.LOSES
    if __wins_on_buying(high, position_value):
        return Evaluation.WINS
    return Evaluation.NONE


def __evaluate_selling(position_value, low, high):
    if __loses_on_selling(high, position_value):
        return Evaluation.LOSES
    if __wins_on_selling(low, position_value):
        return Evaluation.WINS
    return Evaluation.NONE


def __wins_on_buying(high: np.float32, value: np.float32):
    limit = value + _take_profit
    return np.isclose(high, limit, _threshold) or high > limit


def __loses_on_buying(low: np.float32, value: np.float32):
    limit = value - _stop_loss
    return np.isclose(low, limit, _threshold) or low < limit


def __wins_on_selling(low: np.float32, value: np.float32):
    limit = value - _take_profit
    return np.isclose(low, limit, _threshold) or low < limit


def __loses_on_selling(high: np.float32, value: np.float32):
    limit = value + _stop_loss
    return np.isclose(high, limit, _threshold) or high > limit
