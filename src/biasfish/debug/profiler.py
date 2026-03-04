# standard
from typing import Tuple, Callable
import time

TimeElapsed = float

def profile(method: Callable, args: list[any], repeat=1) -> Tuple[TimeElapsed, any]:
    """ Executes a method and returns the runtime and the method outputs

    Args:
        method (Callable): The method to profile
        args (list[any]): The arguments for the method
        repeat (int, optional): The number of times to execute the method. Defaults to 1.

    Returns:
        Tuple[TimeElapsed, any]: Returns the runtime and method outputs
    """
    start_time = time.perf_counter()

    if repeat > 1:
        for _ in range(repeat - 1):
            method(*args)

    output = method(*args)

    time_elapsed = time.perf_counter() - start_time

    return (time_elapsed, output)