from __future__ import annotations

from abc import ABCMeta, abstractmethod
from functools import reduce
from operator import or_
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

from portion.interval import Interval

from .utils import RealField

import portion as interval

class PiecewiseGeneric(metaclass=ABCMeta):
    """
        Abstract base class. 
        
        It defines the contract that the derived class must implement. 


        Attrs:
            - intervals: list of interval objects, that define the
                branched domain of their corresponding callback.
            - funcs: sequence of callables being evaluated as callbacks
                upon activation of their corresponding branch.
    """

    __slots__ = ("__intervals", "__funcs")

    def __init__(self, 
                 branch_intervals: List[interval],
                 branch_clbks: Sequence[Callable[[float], float]],
    ):
        if not isinstance(branch_intervals, Sequence):
            raise TypeError("Branch intervals expects an empty sequence or " \
                            "a sequence of intervals.")

        if not isinstance(branch_clbks, Sequence):
            raise TypeError("Branch callbacks expects an non-empty sequence " \
                            "of callables.")

        if not branch_clbks:
            raise ValueError("branch callbacks must not be empty")

        assert all(isinstance(i, Interval) for i in branch_intervals)
        assert all(hasattr(f, "__call__") for f in branch_clbks)

        assert  0 <= (len(branch_clbks) - len(branch_intervals)) <=1, \
                "Branch callbacks and branch intervals  sequences must be " \
                "equal in length, or in case of an 'otherwise' branch " \
                "the branch callbacks sequence must only have an extra item."

        if (len(branch_clbks) - len(branch_intervals)) == 1:
            otherwise = reduce(or_, branch_intervals or [interval.empty()])

            if not hasattr(branch_intervals, 'append'):
                branch_intervals = list(branch_intervals)

            branch_intervals.append(~otherwise)

        self.__intervals = branch_intervals
        self.__funcs = branch_clbks

    @property
    def intervals(self) -> Sequence[interval]:
        return self.__intervals

    @property
    def funcs(self) -> Sequence[Callable[[float], float]]:
        return self.__funcs

    @abstractmethod
    def __call__(self, x: RealField) -> Iterable[Optional[float]]:
        pass

    @abstractmethod
    def min(self, x: RealField) -> Tuple[int, Optional[float]]:
        pass

    @abstractmethod
    def max(self, x: RealField) -> Tuple[int, Optional[float]]:
        pass

    @classmethod
    @abstractmethod
    def from_funcdef(cls, func: Callable[[float], float]) -> PiecewiseGeneric:
        pass