import numpy as np
from collections.abc import Iterable


class MyDataFrame:
    def __init__(self, columns: Iterable, n_elements: int, dtype=np.float32):
        """
        Data structure used to store key, value pairs. Used instead of a pandas dataframe to
        reduce overhead.

        :param columns: Iterable of columns
        :param n_elements: Number of elements
        :param dtype: Datatype of arrays, defaults to np.float32
        """
        self.n_elements = n_elements
        self.dtype = dtype
        self.index = np.arange(0, n_elements)
        self.columns = set(columns)
        self.data = {col: np.zeros(self.n_elements, dtype=self.dtype) for col in columns}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        if not isinstance(value, np.ndarray):
            raise ValueError("Cannot set a non-numpy array as value")
        if value.shape != self.data[key].shape:
            raise ValueError(f"Dimensions of numpy array does not match definition ({self.n_elements},)")
        if key not in self.columns:
            raise KeyError("The key {} is not defined.".format(key))

        self.data[key] = value

    def filter(self, like):
        """
        Return dictionary with keys containing like.

        :param like:
        :return: Dictionary
        """
        items = [col for col in self.columns if like in col]
        if not items:
            raise ValueError(f"{like} is not in columns")

        return {item: self.data[item] for item in items}

    def __str__(self):
        return str(self.data)
