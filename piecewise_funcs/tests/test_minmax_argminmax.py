from ..piecewise_function import PiecewiseFunc

def test_minmax_argminmax_with_some_nones():
    def func(x: float) -> float:
        if -5 < x < 0 or 1 <= x < 2:
            return -x
        elif x == -6:
            return 7 / 8
        elif 0 <= x < .5:
            return -1

    pd = PiecewiseFunc.from_funcdef(func)

    x = [-6, 2, 3, 5, 5, 7, .3]
    y = [.875, None, None, None, None, None, -1]

    assert [*pd(x)] == y
    assert pd.min(x) == (6, -1)
    assert pd.max(x) == (0, .875)

def test_minmax_argminmax_with_all_nones():
    def func(x: float) -> float:
        if -5 < x < 0 or 1 <= x < 2:
            return -x
        elif x == -6:
            return 7 / 8
        elif 0 <= x < .5:
            return -1

    pd = PiecewiseFunc.from_funcdef(func)

    x = [2, 3, 5, 5, 7]
    y = len(x) * [None]

    assert [*pd(x)] == y
    assert pd.min(x) == (0, None)
    assert pd.max(x) == (0, None)


def test_minmax_argmin_max_all_floats():
    def func(x: float) -> float:
        if x >= 0:
            return x
        return -1.

    pd = PiecewiseFunc.from_funcdef(func)

    x = range(-1, 2)
    y = [-1, 0, 1]

    assert [*pd(x)] == y
    assert pd.min(x) == (0, -1)
    assert pd.max(x) == (2, 1)