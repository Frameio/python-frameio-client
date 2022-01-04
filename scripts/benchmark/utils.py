import sys

from timeit import default_timer as timer


def timefunc(func, *args, **kwargs):
    """Time a function.

    args:
        iterations=3

    Usage example:
        timeit(myfunc, 1, b=2)
    """
    try:
        iterations = kwargs.pop("iterations")
    except KeyError:
        iterations = 3
    elapsed = sys.maxsize
    for _ in range(iterations):
        start = timer()
        result = func(*args, **kwargs)
        elapsed = min(timer() - start, elapsed)
    print(("Best of {} {}(): {:.9f}".format(iterations, func.__name__, elapsed)))
    return result
