from __future__ import annotations

from inspect import getsource
from itertools import combinations, compress, starmap
from math import inf
from operator import and_
from textwrap import dedent
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

from portion.interval import Interval

from .piecewise_generic import PiecewiseGeneric
from .utils import (
    boolop_to_interval,
    MALFORMED_PFUNC_EXCEPTION,
    node_to_func,
    RealField,
)

import ast

class PiecewiseFunc(PiecewiseGeneric):
    """
        Concrete class, represents a piecewise function using a 
        sequence of intervals as each branch's domain and a sequence of
        callables as each branch's evaluation result.
        
        Implements the interface that PiecewiseGeneric exposes, adding
        an extra staticmethod that validates the piecewise function definition,
        a factory method accepting a regular python function representing a
        piecewise function in a more pythonic way.

        Attrs:
            - intervals: list of interval objects, that define the
                branched domain of their corresponding callback.
            - funcs: sequence of callables being evaluated as callbacks
                upon activation of their corresponding branch.

        Methods:
            - min: tuple of int and float, the position at which the minimum
                value occurs in teh sequence (i.e. argmin) and its actual
                float value.

                It expects an object of type RealField, that is a single
                number or an Iterable of floats. Union[float, Iterable[float]]

            - max: tuple of int and float, the position at which the maximum
                value occurs in teh sequence (i.e. argmax) and its actual
                float value.

                It expects an object of type RealField, that is a single
                number or an Iterable of floats. Union[float, Iterable[float]]

            - __apply: iterable of floats or Nones,
                Evaluates teh piecewise function on the given input. If a
                value does not lie on any of branches intervals, then a None
                is returned as the evaluation of the piecewise function,
                otherwise the actual value of the piecewise function is returned.

                It expects an object of type RealField, that is a single
                number or an Iterable of floats. Union[float, Iterable[float]]

            - __call__: iterable of floats or Nones,
                Yields from __apply. An iterator containing the evaluated values, as
                stated in __apply, returned as a result of invoking the object.

                It expects an object of type RealField, that is a single
                number or an Iterable of floats. Union[float, Iterable[float]]

            - from_funcdef: Callable[[float], float],
                Accepts a regular function, parses it, constructs a PiecewiseFunc
                object and returns it to the caller.

                Expects a Callable[[float], float].

                Throws a TypeError if the input does not include a __call__
                method, that is, it isn't a callable.

                Throws a TypeError if the parsed input does not contain an
                ast.FuncDef node containing the name of teh function.

                Throws Exception on illegal syntax.
                The only constructs supported for the input callable are
                'if/elif/else', 'return', logical expressions containing 'and/
                or', compare expressions using '<, >, ==, <=,>='

                Some examples of legal syntax are:

                def f(x):
                    if 1 < x < 2:
                        return 1
                    elif x > 5:
                        return -2*x
                    else:
                        return 3*x - 1

                def g(x):
                    if 1 <= x < 2 or x > 5:
                        return x + 1
                    elif x == -5:
                        return 7/8
                    return 3/4*x

                Some examples of illegal syntax are:

                def h(x):
                    t = 1
                    if x > t:
                        z = some_func(...)
                        return 1
                    else:
                        return abs(x)
                    y = 2

                i = lambda x: x

            - __check_domain_validity: list of intervals,
                Checks if one or more branches intersect each other

                Throws a ValueError if one or more branches intersect each other.
    """

    @staticmethod
    def __bound_key_func(bound: float):
        return lambda pair: pair[1] if pair[1] is not None else bound

    def __init__(self,
                 branch_intervals: List[Interval],
                 branch_clbks: Sequence[Callable[[float], float]],
    ):
        super().__init__(branch_intervals, branch_clbks)
        self.__check_domain_validity(branch_intervals)

    def __call__(self, x: RealField) -> Iterable[Optional[float]]:
        yield from self.__apply(x)

    def min(self, x: RealField) -> Tuple[int, Optional[float]]:
        return min(enumerate(self.__apply(x)), key=self.__bound_key_func(inf))

    def max(self, x: RealField) -> Tuple[int, Optional[float]]:
        return max(enumerate(self.__apply(x)), key=self.__bound_key_func(-inf))

    def __apply(self, x: RealField) -> Iterable[Optional[float]]:
        def _eval(scalar: float) -> Optional[float]:
            sel_func : Callable[[float], Optional[float]]  # for type hinting

            try:
                # select the active branch
                sel_func = next(compress(self.funcs,
                                (float(scalar) in ival for ival in self.intervals)))
            except StopIteration:
                sel_func = lambda _: None  # out of domain callback
            except (TypeError, ValueError) as ex:
                raise TypeError("Input values to piecewise function should " \
                                "either be castable to or subclass type float.") \
                    from ex
            return sel_func(scalar)
                 
        # promote float  to an iterable, e.g. tuple
        if not isinstance(x, Iterable):
            x = (x, )

        yield from (_eval(v) for v in x)

    @staticmethod
    def __check_domain_validity(intervals: List[Interval]):
        if any(starmap(and_, combinations(intervals, 2))):
            raise ValueError("One or more branches have intersecting intervals")

    @classmethod
    def from_funcdef(cls, func: Callable[[float], float]) -> PiecewiseFunc:
        interval_nodes, callback_nodes = [], [] 

        if not hasattr(func, "__call__"):
            raise TypeError("This factory method expects a callable.")

        func_node = ast.parse(dedent(getsource(func))).body[0]

        if not isinstance(func_node, ast.FunctionDef):
            raise TypeError(f"Function {func.__name__} should have a " \
                            "regular function definition with type function")
 
        node: Any = func_node.body.pop(0)

        while node:
            if isinstance(node, ast.If):
                interval_nodes.append(node.test)
                callback_nodes.append(node.body[0])

                if node.orelse:
                    node = node.orelse[0]
                elif func_node.body:
                    node = func_node.body.pop(0)
                else:
                    node = None
            elif isinstance(node, ast.Return):
                callback_nodes.append(node)
                node = None
            else:
                node = None

        if not (interval_nodes or callback_nodes):
            raise MALFORMED_PFUNC_EXCEPTION(func_node.name)

        intervals = [boolop_to_interval(node) for node in interval_nodes]
        callbacks = [node_to_func(node) for node in callback_nodes]

        return cls(intervals, callbacks)