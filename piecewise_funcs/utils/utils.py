from functools import reduce
from itertools import chain
from operator import add, and_, mul, or_, sub, truediv
from typing import Any, Callable, Union

from portion.interval import Interval

import ast
import portion as interval

op_map = {
    ast.And: and_,
    ast.Or: or_,
    ast.Mult: mul,
    ast.Add: add,
    ast.Div: truediv,
    ast.Sub: sub,
}

CMP_ERROR = Exception("Compare expression of x, must be " \
                      " of the form:\n" \
                      "\tx <cmp_op> <constant> or \n" \
                      "\t<constant> <cmp_op> x or \n" \
                      "\t<constant> <cmp_op> x <cmp_op> " \
                      "<constant>")

EXPR_ERROR = Exception("Expression should be a zero or " \
                       "first order polynomial.")

def _to_float(node: Union[ast.UnaryOp, ast.Constant]) -> float:
    if isinstance(node, ast.UnaryOp):
        assert isinstance(node.operand, ast.Constant)

        if isinstance(node.op, ast.USub):
            return -node.operand.value
        elif isinstance(node.op, ast.UAdd):
            return node.operand.value
        else:
            raise TypeError("The only unary ops supported" \
                            "are: USub, UAdd")
    assert isinstance(node, ast.Constant)

    return node.value


def boolop_to_interval(root: ast.expr) -> Interval:
    def _recur(node):
        ival = None

        if isinstance(node, ast.BoolOp):
            return reduce(op_map[type(node.op)], (_recur(v) for v in node.values))

        if isinstance(node, ast.Compare):
            cmp_lst = [s1 for s2 in zip(node.ops, node.comparators) for s1 in s2]

            cmp_lst = [*chain([node.left], cmp_lst)]

            cmp_lst = [s if not isinstance(s, (ast.UnaryOp, ast.Constant)) \
                           else _to_float(s) \
                       for s in cmp_lst]

            if len(cmp_lst) == 5:
                assert isinstance(cmp_lst[2], ast.Name)

                if isinstance(cmp_lst[1], (ast.Lt, ast.LtE)) and \
                        isinstance(cmp_lst[3], (ast.Lt, ast.LtE)):
                    ival = interval.open(cmp_lst[0], cmp_lst[-1])

                    if isinstance(cmp_lst[1], ast.LtE):
                        ival = ival.replace(left=interval.CLOSED)
                    elif isinstance(cmp_lst[3], ast.LtE):
                        ival = ival.replace(right=interval.CLOSED)

                elif isinstance(cmp_lst[1], (ast.Gt, ast.GtE)) and \
                        isinstance(cmp_lst[3], (ast.Gt, ast.GtE)):
                    ival = interval.open(cmp_lst[-1], cmp_lst[0])

                    if isinstance(cmp_lst[1], ast.GtE):
                        ival = ival.replace(right=interval.CLOSED)
                    elif isinstance(cmp_lst[3], ast.GtE):
                        ival = ival.replace(left=interval.CLOSED)
                else:
                    raise CMP_ERROR

            elif len(cmp_lst) == 3:
                if isinstance(cmp_lst[1], (ast.Lt, ast.LtE)):
                    if isinstance(cmp_lst[0], ast.Name):
                        ival = interval.open(-interval.inf, cmp_lst[-1])
                    else:
                        try:
                            ival = interval.open(cmp_lst[0], interval.inf)
                        except AttributeError:
                            raise CMP_ERROR

                    if isinstance(cmp_lst[1], ast.LtE):
                        ival = ival.replace(right=interval.CLOSED, \
                                            left=interval.CLOSED)
                elif isinstance(cmp_lst[1], (ast.Gt, ast.GtE)):
                    if isinstance(cmp_lst[0], ast.Name):
                        ival = interval.open(cmp_lst[-1], interval.inf)
                    else:
                        try:
                            ival = interval.open(-interval.inf, cmp_lst[0])
                        except AttributeError:
                            raise CMP_ERROR

                    if isinstance(cmp_lst[1], ast.GtE):
                        ival = ival.replace(right=interval.CLOSED, \
                                            left=interval.CLOSED)
                elif isinstance(cmp_lst[1], ast.Eq):
                    if isinstance(cmp_lst[0], ast.Name):
                        ival = interval.singleton(cmp_lst[-1])
                    else:
                        ival = interval.singleton(cmp_lst[0])
                elif isinstance(cmp_lst[1], ast.NotEq):
                    if isinstance(cmp_lst[0], ast.Name):
                        ival = interval.signleton(cmp_lst[-1])
                    else:
                        ival = interval.singleton(cmp_lst[0])
                    ival = ~ival
                else:
                    raise CMP_ERROR

            else:
                raise CMP_ERROR

        return ival or interval()

    if not isinstance(root, (ast.BoolOp, ast.Compare)):
        raise Exception("Logical expression of x, must only " \
                        "use boolops, i.e. 'and' & 'or'")

    return _recur(root)


def node_to_func(root: Any) -> Callable[[float], float]:
    def _func(x: float) -> float:
        def _recur(node):
            if isinstance(node, ast.Constant):
                return _to_float(node)
            elif isinstance(node, ast.UnaryOp):
                if isinstance(node.operand, ast.Name):
                    return -x
                return _to_float(node)
            elif isinstance(node, ast.Name):
                return x
            elif isinstance(node, ast.BinOp):
                try:
                    op = op_map[type(node.op)]
                except KeyError as e:
                    raise EXPR_ERROR from e
                else:
                    return op(_recur(node.left), _recur(node.right))
            else:
                raise EXPR_ERROR

        return _recur(root.value)

    assert isinstance(root, ast.Return)

    return _func
