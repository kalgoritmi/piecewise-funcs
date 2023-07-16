from ..piecewise_function import PiecewiseFunc

import portion as p
import pytest


def test_apply_fully_defined():
    pw = PiecewiseFunc(
        [p.open(-p.inf, 0), p.closedopen(0, p.inf)],
        [lambda x: -x, lambda x: 1.],
    )

    x = [-20, 0, 20]
    y = [20., 1., 1.]

    assert [*pw(x)] == y

def test_apply_with_out_of_domain_input():
    pw = PiecewiseFunc(
        [p.open(1, 2), p.closedopen(-1, 0), p.openclosed(2, 3)],
        [lambda x: x, lambda x: 1., lambda x: 2*x+1],
    )

    x = [-2, -.5, 0, 1.5, 2.5, 3, 4]
    y = [None, 1., None, 1.5, 6., 7., None]

    assert [*pw(x)] == y

def test_apply_with_implicit_complementary_branch():
    pw = PiecewiseFunc(
        [p.open(1, 2), p.closedopen(-1, 0)],
        [lambda x: x, lambda x: 1., lambda x: 2*x+1],
    )

    x = [-.5, 0, 1.5, 2]
    y = [1., 1., 1.5, 5.]

    assert [*pw(x)] == y

def test_empty_branch_intervals_arg():
    pw = PiecewiseFunc([], [lambda x: x])

    assert pw.intervals == [p.open(-p.inf, p.inf)]
    assert [*pw(range(-1,1))] == [*range(-1, 1)]

def test_empty_branch_callbacks_arg():
    with pytest.raises(ValueError):
        PiecewiseFunc([], [])

def test_2_or_more_extra_branch_callbacks():
    with pytest.raises(AssertionError):
        PiecewiseFunc(
            [p.open(1, 2)],
            [lambda x: x, lambda x: 1., lambda x: 2 * x + 1],
        )

    with pytest.raises(AssertionError):
        PiecewiseFunc(
            [],
            [lambda x: x, lambda x: 1., lambda x: 2 * x + 1, lambda x: 0.],
        )

def test_intersecting_intervals():
    def func(x: float) -> float:
        if x >= 0:
            return 1
        elif x < 1:
            return 0

    with pytest.raises(ValueError):
        PiecewiseFunc.from_funcdef(func)

def test_runtime_illegal_input_vector_of_none():
    pw = PiecewiseFunc([], [lambda x: x])

    with pytest.raises(TypeError):
        result = [*pw(3*[None])]

def test_runtime_illegal_branch_intervals_seq():
    with pytest.raises(AssertionError):
        PiecewiseFunc([None, None], [lambda x: x, lambda x: 1])

    with pytest.raises(TypeError):
        PiecewiseFunc(None, [lambda x: x, lambda x: 1])

    with pytest.raises(TypeError):
        PiecewiseFunc([], None)


    # this should not raise an AssertionError
    try:
        pw = PiecewiseFunc([], [lambda x: x])
    except AssertionError as ae:
        assert False, f"Raised an assertion error {ae}"

def test_runtime_illegal_branch_callbacks_seq():
    with pytest.raises(AssertionError):
        pw = PiecewiseFunc([~p.empty(),], [None, None])