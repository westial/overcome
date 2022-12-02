"""
cposition package entry point. cposition is a c-like high performance approach
to get the buying and selling earnings overcome.
"""
import numpy as np

from src.overcome.position.buying import Buying
from src.overcome.position.position import Position
from src.overcome.position.positions import Positions
from src.overcome.position.selling import Selling


def calculate_earnings(
        high_low_close: np.ndarray,
        take_profit,
        stop_loss,
        create_position: callable):
    earn_buying = np.zeros([len(high_low_close), 1], dtype=np.float32)
    earn_selling = np.zeros([len(high_low_close), 1], dtype=np.float32)
    buying: Positions = Buying()
    selling: Positions = Selling()
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
            buying,
            selling)
        __collect(index, row[2], create_position, buying, selling)
    return earn_buying, earn_selling


def __set_earnings(high, low, tp, sl, earn_buying, earn_selling, buying, selling):
    earn_buying = buying.update(low, high, tp, sl, earn_buying)
    earn_selling = selling.update(low, high, tp, sl, earn_selling)
    return earn_buying, earn_selling


def __collect(index, close, create_position: callable, buying, selling):
    position: Position = create_position(index, close)
    buying.insert(position)
    selling.insert(position)
