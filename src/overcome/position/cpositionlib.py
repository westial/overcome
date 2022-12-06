"""
Facade of the cposition package. cposition is a c-like high performance
approach to get the buying and selling earnings overcome.

FIXME Temporarily I changed from pyx to py in order to gain on development speed
"""
import numpy as np

from src.overcome.position.evaluation import Evaluation

POSITION_INDEX = 0
POSITION_VALUE = 1
THRESHOLD = np.float32(0.00001)

stop_loss = 0.0
take_profit = 0.0

earn_buying = None
earn_selling = None

open_buying = set()
open_selling = set()


def __initialize(high_low_close: np.ndarray, take_profit_, stop_loss_):
    global take_profit, stop_loss, \
        earn_buying, earn_selling, \
        open_buying, open_selling
    take_profit = take_profit_
    stop_loss = stop_loss_
    earn_buying = np.zeros([len(high_low_close), 1], dtype=np.float32)
    earn_selling = np.zeros([len(high_low_close), 1], dtype=np.float32)
    open_buying = set()
    open_selling = set()


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
    return earn_buying, earn_selling


def __set_earnings(high, low):
    global earn_buying, earn_selling, open_buying, open_selling
    earn_buying = __update(low, high, earn_buying, open_buying, __evaluate_buying)
    earn_selling = __update(low, high, earn_selling, open_selling, __evaluate_selling)


def __collect(index, close):
    global open_buying, open_selling
    position: tuple = (index, close)
    open_buying.add(position)
    open_selling.add(position)


def __update(
        low,
        high,
        data: np.ndarray,
        open_positions: set,
        evaluate: callable):
    remaining_positions = set()
    while len(open_positions):
        position = open_positions.pop()
        overcome = evaluate(position[POSITION_VALUE], low, high)
        if Evaluation.WINS == overcome:
            data[position[POSITION_INDEX]] = take_profit
        elif Evaluation.LOSES == overcome:
            data[position[POSITION_INDEX]] = stop_loss * (-1)
        else:
            remaining_positions.add(position)
    open_positions.update(remaining_positions)
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
    limit = value + take_profit
    return np.isclose(high, limit, THRESHOLD) or high > limit


def __loses_on_buying(low: np.float32, value: np.float32):
    limit = value - stop_loss
    return np.isclose(low, limit, THRESHOLD) or low < limit


def __wins_on_selling(low: np.float32, value: np.float32):
    limit = value - take_profit
    return np.isclose(low, limit, THRESHOLD) or low < limit


def __loses_on_selling(high: np.float32, value: np.float32):
    limit = value + stop_loss
    return np.isclose(high, limit, THRESHOLD) or high > limit