import time
from typing import Any, Callable


def calculate_running_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that calculates the running time of the given function.

    Args:
        func (Callable[..., Any]): The function to be timed.

    Returns:
        Callable[..., Any]: The wrapped function.
    """

    def wrapper(*args, **kwargs) -> Any:
        start_time: float = time.perf_counter()
        result: Any = func(*args, **kwargs)
        end_time: float = time.perf_counter()
        print(end_time - start_time)
        return result

    return wrapper
