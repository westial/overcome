from unittest import TestCase

import numpy as np
import pandas as pd

from src.overcome.overcome import Overcome


class TestOvercome(TestCase):
    def test_it_counteracts_selling_with_buying(self):
        df = pd.read_csv(
            "../samples/few_live1m_histdata.csv",
            sep=";",
            index_col=0,
            parse_dates=True,
            names=['date', 'open', 'high', 'low', 'close', 'volume']
        ).sort_index()
        overcome = Overcome(
                np.float32(0.00001),
                np.float32(0.001),
                np.float32(0.001)
            )
        high_low_close = df[["high", "low", "close"]].to_numpy(dtype=np.float32)
        (df["earn_buying"], df["earn_selling"]) = overcome.apply(high_low_close)
        assert df["earn_buying"].sum() == df["earn_selling"].sum() * (-1)

    def test_it_applies_on_a_large_dataframe(self):
        df = pd.read_parquet("../samples/live15m.parquet").sort_index()
        overcome = Overcome(
                np.float32(0.00001),
                np.float32(0.001),
                np.float32(0.001)
            )
        df_part = df[:100000]
        high_low_close = df_part[["high", "low", "close"]].to_numpy(dtype=np.float32)
        (df_part["earn_buying"], df_part["earn_selling"]) = overcome.apply(high_low_close)
        assert True
