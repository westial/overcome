from operator import itemgetter

import numpy as np
import pandas as pd

from overcome.calculator.outcomeprofits import OutcomeProfits
from overcome.overcome import Overcome


class Analysis:
    def __init__(
            self,
            position_threshold: np.float32,
            take_profit: np.float32,
            stop_loss: np.float32,
            categories: dict):
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

    def apply(self, predicted: pd.Series, ohlcv: pd.DataFrame):
        data = ohlcv.copy(deep=True)
        overcome = Overcome(self.__threshold, self.__tp, self.__sl)
        (data["earn_buying"], data["earn_selling"]) = overcome.apply(
            ohlcv[["high", "low", "close"]].to_numpy(dtype=np.float32)
        )
        missing_index = predicted.index.difference(data.index)
        same_index_data = data[~data.index.isin(missing_index)]
        same_index_data["operation"] = predicted
        return self.__outcome_profits.calculate(same_index_data)
