import pandas as pd

from overcome.minimizer.costminimizer import CostMinimizer
from overcome.minimizer.invalidminimization import InvalidMinimization


class RegularCostMinimizer(CostMinimizer):
    def __init__(
            self,
            relax_category: int,
            relax_interval: int,
            offset=0):
        self.__offset = offset
        if not relax_interval or offset > relax_interval:
            raise InvalidMinimization()
        self.__interval = relax_interval
        self.__relax_category = relax_category

    def minimize(self, operations: pd.Series) -> pd.Series:
        kept_operations = operations.iloc[self.__offset::self.__interval + 1]
        results = pd.Series(
            index=operations.index, dtype=int
        ).fillna(self.__relax_category)
        results.update(kept_operations)
        return results
