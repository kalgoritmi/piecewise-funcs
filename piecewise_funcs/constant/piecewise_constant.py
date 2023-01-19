import os
import sys
from typing import Callable, List, Tuple

sys.path.append(os.path.abspath(r".."))
from piecewise_generic import PiecewiseFunc

class PiecewiseConstant(PiecewiseFunc):

    def __init__(self,
                 predicate_clbks: List[Callable[[float], float]],
                 callable_clbks: List[Callable[[float], float]],
    ):
        super().__init__(predicate_clbks, callable_clbks)

