from abc import ABC, abstractmethod

import pandas as pd


class CostMinimizer(ABC):
    @abstractmethod
    def minimize(self, operations: pd.Series) -> pd.Series:
        pass
