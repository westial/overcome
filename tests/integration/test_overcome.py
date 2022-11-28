from unittest import TestCase

import numpy as np
import pandas as pd

from src.overcome.overcome import Overcome
from src.overcome.position.buying import Buying
from src.overcome.position.precisefactory import PreciseFactory
from src.overcome.position.selling import Selling


class TestOvercome(TestCase):
    def test_it_counteracts_selling_with_buying(self):
        df = pd.read_csv(
            "../samples/few_live1m_histdata.csv",
            sep=";",
            index_col=0,
            parse_dates=True,
            names=['date', 'open', 'high', 'low', 'close', 'volume']
        ).sort_index()
        position_factory = PreciseFactory(precision_threshold=0.00001)
        overcome = Overcome(
            position_factory,
            np.float64(0.001),
            np.float64(0.001),
            Buying(),
            Selling())
        result = overcome.apply(df)
        assert result["earn_buying"].sum() == result["earn_selling"].sum() * (-1)

    def test_it_applies_on_a_large_dataframe(self):
        df = pd.read_parquet("../samples/live15m.parquet").sort_index()
        position_factory = PreciseFactory(precision_threshold=0.00001)
        overcome = Overcome(
            position_factory,
            np.float64(0.005),
            np.float64(0.0005),
            Buying(),
            Selling())
        result = overcome.apply(df[:10000])
        assert False
