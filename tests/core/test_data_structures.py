import pytest
import numpy as np
from core.data_structures import MyDataFrame

@pytest.fixture()
def simple_data_frame():
    return MyDataFrame(columns=["aa", "ab", "bc"], n_elements=3)
    

def test_constructor(simple_data_frame):
    
    columns = ["aa", "ab", "bc"]
    dtype = np.float32
    n_elements = 3
    assert simple_data_frame.n_elements == n_elements
    assert simple_data_frame.dtype == dtype
    np.testing.assert_array_equal(simple_data_frame.index, np.arange(0, n_elements))
    assert simple_data_frame.columns == set(columns)
    
    expected = {col: np.zeros(n_elements, dtype=dtype) for col in columns}
    for col in columns:
        np.testing.assert_array_equal(simple_data_frame.data[col], expected[col])


def test_getitem(simple_data_frame):
    expected = np.zeros((3))
    actual = simple_data_frame["aa"]
    
    np.testing.assert_equal(expected, actual)

def test_setitem(simple_data_frame):
    expected = np.ones(3) * 2
    simple_data_frame["aa"] = expected

    np.testing.assert_equal(expected, simple_data_frame["aa"])

    with pytest.raises(ValueError):
        simple_data_frame["aa"] = 2

    with pytest.raises(ValueError):
        simple_data_frame["ab"] = np.zeros(666)

    with pytest.raises(KeyError):
        simple_data_frame["aaa"] = np.zeros(3)

def test_filter(simple_data_frame):
    expected = {
        "aa": np.zeros(3), 
        "ab": np.zeros(3)}

    actual = simple_data_frame.filter("a")

    for c1, c2 in zip(expected, actual):
        np.testing.assert_equal(expected[c1], actual[c1])
        np.testing.assert_equal(expected[c2], actual[c2])
    
    expected = {
        "bc": np.zeros(3), 
    }

    actual = simple_data_frame.filter("c")

    for c1, c2 in zip(expected, actual):
        np.testing.assert_equal(expected[c1], actual[c1])
        np.testing.assert_equal(expected[c2], actual[c2])

def test_filter_empty(simple_data_frame):
    
    with pytest.raises(ValueError):
        actual = simple_data_frame.filter("xy")


def test_sum_column(simple_data_frame):
    simple_data_frame["aa"] = np.ones(3)
    expected = 3
    actual = simple_data_frame["aa"].sum()

    assert expected == actual