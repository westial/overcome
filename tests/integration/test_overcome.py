from unittest import TestCase

import numpy as np
import pandas as pd

from src.overcome.overcome import Overcome


class TestOvercome(TestCase):
    def test_it_counteracts_selling_with_buying(self):
        """
        NOTE Test spends 496ms
        """
        df = pd.read_csv(
            "../samples/few_live1m_histdata.csv",
            sep=";",
            index_col=0,
            parse_dates=True,
            names=['date', 'open', 'high', 'low', 'close', 'volume']
        ).sort_index()
        overcome = Overcome(
            np.float32(0.001),
            np.float32(0.001))
        result = overcome.apply(df)
        assert result["earn_buying"].sum() == result["earn_selling"].sum() * (-1)

    def test_it_applies_on_a_large_dataframe(self):
        """
        NOTE Test spends 1 min 18 sec
        """
        df = pd.read_parquet("../samples/live15m.parquet").sort_index()
        overcome = Overcome(
            np.float32(0.005),
            np.float32(0.0005))
        overcome.apply(df[:10000])
        assert True
