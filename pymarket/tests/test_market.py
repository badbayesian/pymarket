import pytest
import pymarket
import numpy as np


if __name__ == "__main__":
    y = np.random.normal(1)
    x = pymarket.Market(n_sellers=1, n_buyers=1, rounds=10000)
    print(x)
