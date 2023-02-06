from ..piecewise_function import PiecewiseFunc

import portion as p
import pytest

def test_illegal_arg():
    with pytest.raises(TypeError, match=r"expects a callable"):
        pw = PiecewiseFunc.from_funcdef(None)

def test_simple_return():
    def ret_const(_: float) -> float:
        return 6.

    def ret_lin(x: float) -> float:
        return 2*x + 1

    pw_const = PiecewiseFunc.from_funcdef(ret_const)
    pw_lin = PiecewiseFunc.from_funcdef(ret_lin)

    assert pw_const.intervals == [p.open(-p.inf, p.inf)]
    assert pw_lin.intervals == [p.open(-p.inf, p.inf)]

    assert next(pw_const(1)) == 6.
    assert next(pw_lin(1)) == 3.


def test_mixed_case():
    def mixed_func(x: float) -> float:
        if -5 < x < 0 or 1 <= x < 2:
            return 2
        elif x == -6:
            return 7 / 8
        elif x < .5 and x > 0:
            return -1

    pw = PiecewiseFunc.from_funcdef(mixed_func)

    branch_intervals = [
        p.open(-5, 0) | p.closedopen(1, 2),
        p.singleton(-6),
        p.open(0, .5),
    ]

    assert pw.intervals == branch_intervals

    x = [-4, -6, .3, 10]
    y = [2, 7/8, -1, None]

    assert [*pw(x)] == y

def test_or_chain():
    def func(x: float) -> float:
        if x == 5 or x < -4 or 20 > x >= 10 or x == -0.2:
            return .25

    pw = PiecewiseFunc.from_funcdef(func)

    ival = p.singleton(5) | p.open(-p.inf, -4) | p.closedopen(10, 20) | p.singleton(-.2)

    assert pw.intervals == [ival]

    x = [5, -20, 0, 15, -.2]
    y = [.25, .25, None, .25, .25]

    assert [*pw(x)] == y

def test_and_chain():
    def func(x: float) -> float:
        if  x < -4 and -10 <= x < 5 and x > -5:
            return .25

    pw = PiecewiseFunc.from_funcdef(func)

    assert pw.intervals == [p.open(-5, -4)]

    x = [-20, 0, -4.78]
    y = [None, None, .25]

    assert [*pw(x)] == y

def test_boolop_chain():
    def func(x: float) -> float:
        if  x < -4 and -10 <= x < 5 and x > -5 or x > 5:
            return .25

    pw = PiecewiseFunc.from_funcdef(func)

    assert pw.intervals == [p.open(-5, -4) | p.open(5, p.inf)]

    x = [-4.25, 10, 0]
    y = [.25, .25, None]

    assert [*pw(x)] == y

def test_empty_chain():
    def func(x: float) -> float:
        if x == 5 and x < -4 and 20 > x >= 10 and x == -0.2:
            return .25

    pw = PiecewiseFunc.from_funcdef(func)

    assert pw.intervals == [p.empty()]

    x = [5, -20, 0, 15, -.2]
    y = len(x) * [None]

    assert [*pw(x)] == y

def test_expanded_linear():
    def func(x: float) -> float:
        if x > 0:
            return -5 - 10/2*x
        return 9*x - 6./3. - 8.5*x

    pw = PiecewiseFunc.from_funcdef(func)

    assert pw.intervals == [p.open(0, p.inf), p.openclosed(-p.inf, 0)]

    x = [1, 5, -2, 0]
    y = [-10, -30, -3, -2]

    assert [*pw(x)] == y

def test_lambda_arg_exception():
    func = lambda x: x

    with pytest.raises(TypeError, match=r"regular function"):
        pw = PiecewiseFunc.from_funcdef(func)

def test_long_ifelse():
    def func(x: float) -> float:
        if 1 <= x < 2:
            return 1.
        elif 2 <= x < 3:
            return 2.
        elif 3 <= x < 4:
            return 3.
        elif 4 <= x < 5:
            return 4.
        else:
            return 1 + 2*x

    pw = PiecewiseFunc.from_funcdef(func)

    branch_intervals = [p.closedopen(i, i+1) for i in range(1, 5)]
    branch_intervals.append(p.open(-p.inf, 1) | p.closedopen(5, p.inf))

    assert pw.intervals == branch_intervals

    x = [1, 2, 3, 4, -1]
    y = [1, 2, 3, 4, -1]

    assert [*pw(x)] == y

def test_ifelif():
    def func(x: float) -> float:
        if 1. <= x < 2.:
            return 1.
        elif 2. <= x < 3.:
            return 2.

    pw = PiecewiseFunc.from_funcdef(func)

    branch_intervals = [
        p.closedopen(1., 2.),
        p.closedopen(2., 3.),
    ]

    assert pw.intervals == branch_intervals

    x = [0, 1., 2., 3.]
    y = [None, 1., 2., None]

    assert [*pw(x)] == y

def test_ifelif_return():
    def func(x: float) -> float:
        if 1. <= x < 2.:
            return x
        elif 2. <= x < 3.:
            return 2. - x
        return -x + 1

    pw = PiecewiseFunc.from_funcdef(func)

    branch_intervals = [
        p.closedopen(1., 2.),
        p.closedopen(2., 3.),
        p.open(-p.inf, 1) | p.closedopen(3., p.inf),
    ]

    assert pw.intervals == branch_intervals

    x = [0, 1., 2., 3.]
    y = [1., 1., 0., -2.]

    assert [*pw(x)] == y

def test_unreachable_return():
    def func(x: float) -> float:
        if 1. <= x < 2.:
            return x
        elif 2. <= x < 3.:
            return 2. - x
        else:
            return -2*x
        return -x + 1

    pw = PiecewiseFunc.from_funcdef(func)

    branch_intervals = [
        p.closedopen(1., 2.),
        p.closedopen(2., 3.),
        p.open(-p.inf, 1) | p.closedopen(3., p.inf),
    ]

    assert pw.intervals == branch_intervals

    x = [0, 1., 2., 3.]
    y = [0, 1., 0., -6.]

    assert [*pw(x)] == y

def test_malformed_func():
    def func(x: float) -> float:
        t = -1
        if x > 0:
            return 0.
        y = abs(t)
        return 7.

    with pytest.raises(Exception, match=r"^Function"):
        PiecewiseFunc.from_funcdef(func)

def test_malformed_compare_expression():
    def func(x: float) -> float:
        if 2 > abs(x) > 0:
            return 0.
        return 7.

    with pytest.raises(Exception):
        PiecewiseFunc.from_funcdef(func)

def test_illegal_return_expressions():
    def func(x: float) -> float:
        if 2 > x > 0:
            return abs(x)
        return x**2

    pw=PiecewiseFunc.from_funcdef(func)

    with pytest.raises(Exception):
        eval_result = [*pw([1,2])]