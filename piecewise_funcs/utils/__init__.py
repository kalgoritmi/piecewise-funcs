from typing import Iterable, Union

from .utils import boolop_to_interval, node_to_func

RealField = Union[float, Iterable[float]]

MALFORMED_PFUNC_EXCEPTION = lambda func_name: \
    Exception(f"Function {func_name}'s definition " \
              "should be of the form:\n" \
              "\tdef func(x: float) -> float:\n" \
              "\t\tif <logical expression of x>:\n" \
              "\t\t\treturn <expression of x>\n" \
              "\t\telif <logical expression of x>:\n" \
              "\t\t\treturn <expression of x>\n" \
              "\t\telse:\n" \
              "\t\t\treturn <expression of x>\n")
