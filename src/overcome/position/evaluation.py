from enum import Enum


class Evaluation(Enum):
    BUY_WINS = 2
    SELL_WINS = 1
    NONE = 0
    SELL_LOSES = -1
    BUY_LOSES = -2

