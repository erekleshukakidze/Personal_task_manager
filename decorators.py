import time
from functools import wraps

from exceptions import TaskManagerError


def handle_errors(func):
    """Catch Task Manager errors and show a friendly message."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TaskManagerError as err:
            print(f"Error: {err}")
        except Exception as err:
            print(f"Unexpected error: {err}")
    return wrapper


def retry(times=3, delay=0.5):
    """Call the function again if it raises OSError"""
    if times < 1:
        raise ValueError("times must be at least 1")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except OSError as err:
                    if attempt == times:
                        raise
                    print(f"Attempt {attempt} failed: {err}")
                    time.sleep(delay)
        return wrapper
    return decorator


def log_action(func):
    """Print when a function starts and finishes, and how long it took."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] {func.__name__} started")
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            print(f"[LOG] {func.__name__} finished in {elapsed:.3f}s")
    return wrapper


