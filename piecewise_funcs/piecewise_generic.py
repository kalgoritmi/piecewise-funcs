from __future__ import annotations

from abc import ABCMeta, abstractmethod
from itertools import compress
from typing import Callable, Iterable, List, Tuple, Union

RealField = Union[float, Iterable[float]]

class PiecewiseFunc(metaclass=ABCMeta):
    """
        Abstract interface class of all piecewise functions types defined,
        as their own modules.
        
        It defines the contract that each derived class must implement. 


        Attrs:
            - preds: list of callables that return a logical
                expression corresponding to a callable in funcs
            - funcs: list of callables being evaluated when
                the corresponding predicate is truthful.
    """

    def __init__(self, 
                 predicate_clbks: List[Callable[[float], float]],
                 func_clbks: List[Callable[[float], float]],
    ):
        self.preds = predicate_clbks
        self.funcs = func_clbks

    def __call__(self, x: RealField ) -> Iterable[float]:
        return self._apply_(x)


    def min(self, x: RealField) -> Tuple[int, float]:
        return min(enumerate(self._apply_(x)), key=lambda pair: pair[1])

    def max(self, x: RealField) -> Tuple[int, float]:
        return max(enumerate(self._apply_(x)), key=lambda pair: pair[1])

    def _apply_(self, x: RealField) -> Iterable[float]:
        def _eval(scalar: float) -> float:
            sel_funcs = [*compress(self.funcs, 
                                   (pred(scalar) for pred in self.preds))]

            if len(sel_funcs) != 1:
                raise ValueError("Exactly one branch of the piecewise function's" \
                                 " domain must be truthful at a time.")
            
            return sel_funcs[0](scalar)
        
        
        # promote scalar to an iterable tuple
        if not isinstance(x, Iterable):
            x = (x, )

        yield from map(_eval, x)

    @classmethod
    @abstractmethod
    def from_pyfunc(cls, pyfunc: Callable[[float], float]) -> PiecewiseFunc:
        pass
