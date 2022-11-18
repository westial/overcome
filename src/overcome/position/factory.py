from abc import ABC, abstractmethod

import numpy as np


class Factory(ABC):
    @abstractmethod
    def create(self, index, value: np.float64):
        pass
