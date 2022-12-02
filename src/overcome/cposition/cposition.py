"""
cposition package entry point. cposition is a c-like high performance approach
to get the buying and selling earnings overcome.
"""
import numpy as np

from src.overcome.position.evaluation import Evaluation
from src.overcome.position.position import Position


def calculate_earnings(
        high_low_close: np.ndarray,
        take_profit,
        stop_loss,
        create_position: callable):
    earn_buying = np.zeros([len(high_low_close), 1], dtype=np.float32)
    earn_selling = np.zeros([len(high_low_close), 1], dtype=np.float32)
    open_buying = set()
    open_selling = set()
    market_values_iterator = np.nditer(
        high_low_close,
        order='C',
        flags=['external_loop'])
    for index, row in enumerate(market_values_iterator):
        __set_earnings(
            row[0],
            row[1],
            take_profit,
            stop_loss,
            earn_buying,
            earn_selling,
            open_buying,
            open_selling)
        __collect(index, row[2], create_position, open_buying, open_selling)
    return earn_buying, earn_selling


def __set_earnings(high, low, tp, sl, earn_buying, earn_selling, open_buying, open_selling):
    earn_buying = __update(low, high, tp, sl, earn_buying, open_buying, __evaluate_buying)
    earn_selling = __update(low, high, tp, sl, earn_selling, open_selling, __evaluate_selling)
    return earn_buying, earn_selling


def __collect(index, close, create_position: callable, open_buying, open_selling):
    position: Position = create_position(index, close)
    open_buying.add(position)
    open_selling.add(position)


def __update(
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
    open_positions.update(remaining_positions)
    return data


def __evaluate_buying(position, low, high, tp, sl):
    return position.evaluate_buying(low, high, tp, sl)


def __evaluate_selling(position, low, high, tp, sl):
    return position.evaluate_selling(low, high, tp, sl)