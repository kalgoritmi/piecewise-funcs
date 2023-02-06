from random import sample
from timeit import timeit

from ..piecewise_function import PiecewiseFunc

def test_timing_piecewise_constant(ratio_tol=1):
    def func(x: float) -> float:
        if x >= 0:
            return 1
        else:
            return 0

    pw = PiecewiseFunc.from_funcdef(func)

    step, timings = 2, []
    for i in range(10, 20, step):
        bound = 1 << i
        x = sample(range(-bound, bound), bound)
        timings.append(timeit('[*pw(x)]', number=20, globals=locals()))

    timing_diffs = [n/p for p, n in zip(timings[:-1], timings[1:])]

    avg_ratio = sum(timing_diffs) / len(timing_diffs)

    # assert O(N) for a piecewise constant function
    assert abs(avg_ratio - (1<<step)) <= ratio_tol


def test_timing_piecewise_linear(ratio_tol=1):
    def func(x: float) -> float:
        if x >= 0:
            return 2*x+1
        else:
            return -x

    pw = PiecewiseFunc.from_funcdef(func)

    step, timings = 2, []
    for i in range(10, 20, step):
        bound = 1 << i
        x = sample(range(-bound, bound), bound)
        timings.append(timeit('[*pw(x)]', number=20, globals=locals()))

    timing_diffs = [n/p for p, n in zip(timings[:-1], timings[1:])]

    avg_ratio = sum(timing_diffs) / len(timing_diffs)

    # assert O(N) for a piecewise linear function
    assert abs(avg_ratio - (1<<step)) <= ratio_tol