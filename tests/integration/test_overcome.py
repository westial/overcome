import unittest
from os.path import dirname
from unittest import TestCase

import numpy as np
import pandas as pd

from overcome.analysis import Analysis
from overcome.overcome import Overcome


class TestOvercome(TestCase):
    def setUp(self):
        self.__relax_category = 0
        self.__sell_category = 1
        self.__buy_category = 2

    def test_it_counteracts_selling_with_buying_outcomes(self):
        df = pd.read_csv(
            f'{dirname(__file__)}/../samples/few_live1m_histdata.csv',
            sep=";",
            index_col=0,
            parse_dates=True,
            names=['date', 'open', 'high', 'low', 'close', 'volume']
        ).sort_index()
        overcome = Overcome(
                np.float32(0.00001),
                np.float32(0.001),
                np.float32(0.001),
                has_counters=True
            )
        high_low_close = df[["high", "low", "close"]].to_numpy(dtype=np.float32)
        (df["earn_buying"], df["earn_selling"], df["buying_lengths"], df["selling_lengths"]) = overcome.apply(high_low_close)
        assert df["earn_buying"].sum() == df["earn_selling"].sum() * (-1)
        print(df.head(30))

    def test_profits_match_between_overcome_and_analysis(self):
        tp = np.float32(0.001)
        sl = np.float32(0.001)
        threshold = np.float32(0.00001)
        df = pd.read_parquet(f'{dirname(__file__)}/../samples/live15m.parquet').sort_index().iloc[-5000:]
        overcome = Overcome(threshold, tp, sl, positions_limit=5)
        high_low_close = df[["high", "low", "close"]].to_numpy(dtype=np.float32)
        (df["earn_buying"], df["earn_selling"]) = overcome.apply(high_low_close)
        df["operations"] = self.__classify_earnings(df["earn_buying"], df["earn_selling"])
        df["positive_earnings_buying"] = df["earn_buying"].clip(lower=0)
        df["positive_earnings_selling"] = df["earn_selling"].clip(lower=0)
        overcome_profits = df["positive_earnings_buying"].add(df["positive_earnings_selling"])
        analysis = Analysis(threshold, tp, sl, {
            "relax": self.__relax_category,
            "sell": self.__sell_category,
            "buy": self.__buy_category
        })
        analysis_results = analysis.apply(df["operations"], df)
        analysis_profits = analysis_results["profits_buying"].add(analysis_results["profits_selling"])
        assert 0 < analysis_profits.sum()
        assert np.all(np.isclose(analysis_profits, overcome_profits))


    def __classify_earnings(self, earn_buying, earn_selling):
        buying_interests = self.__are_interesting(earn_buying)
        selling_interests = self.__are_interesting(earn_selling)
        conditions = [buying_interests, selling_interests]
        categories = [self.__buy_category, self.__sell_category]
        return np.select(conditions, categories, default=self.__relax_category)

    @staticmethod
    def __are_interesting(values: pd.Series):
        return values > 0

    def test_it_applies_on_a_large_dataframe(self):
        df = pd.read_parquet(f'{dirname(__file__)}/../samples/live15m.parquet').sort_index()
        overcome = Overcome(
                np.float32(0.00001),
                np.float32(0.001),
                np.float32(0.001)
            )
        df_part = df[:100000]
        high_low_close = df_part[["high", "low", "close"]].to_numpy(dtype=np.float32)
        (df_part["earn_buying"], df_part["earn_selling"]) = overcome.apply(high_low_close)
        assert True


if __name__ == '__main__':
    unittest.main()
