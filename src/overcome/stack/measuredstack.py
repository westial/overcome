import numpy as np
import pandas as pd

from overcome.stack.stack import Stack, Node


class MeasuredStack(Stack):
    def __init__(self, lengths: pd.Series):
        super().__init__()
        self.__lengths = lengths

    def add(self, content, priority):
        """
        Add a new node into the stack, increase by one all the currently
        existing length records, and initialize a new length record at 0
        indexed by the value in the given content

        :param content: of the stack node and index of the lengths at the same
        time
        :param priority: of the stack
        """
        super().add(content, priority)
        self.__lengths += 1
        self.__lengths.loc[content] = np.int16(0)

    def __remove_length(self, node: Node):
        if node:
            self.__lengths.drop(labels=node.content, inplace=True)

    def shift(self):
        node = super().shift()
        self.__remove_length(node)
        return node

    def pop(self):
        node = super().pop()
        self.__remove_length(node)
        return node

    def length_of(self, index):
        return self.__lengths.loc[index]






