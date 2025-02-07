from time import sleep
from typing import Callable


def retry[
    T
](
    func: Callable[[], T],
    until: Callable[[T], bool] = bool,
    max_wait_s: float = 1.0,
    min_wait_s: float = 0.01,
) -> (T | None):
    """
    Retry func, with exponential backoff

    func: the function which will we tried multiple times
    until: whether to wait until func returns expected value (default: True)
    max_wait_s: max wait time in seconds (default: 1.0)
    min_wait_s: min wait time in seconds (default: 0.01)
    """
    assert min_wait_s <= max_wait_s
    total = t = min_wait_s
    while True:
        assert total <= max_wait_s
        if until(rv := func()):
            return rv
        sleep(t)
        total += t
        t *= 2
