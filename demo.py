from piecewise_funcs import PiecewiseFunc

def demo_func(x: float) -> float:
    if x < 0:
        return -x
    elif x == 6:
        return 7 / 8
    return 5

if __name__ == "__main__":
    pd = PiecewiseFunc.from_funcdef(demo_func)

    ex = [-6, 2, 3, 5, 5, 7, .3]

    print(*pd(ex))
    print(pd.max(ex))
    print(pd.min(ex))
    print(pd.intervals)