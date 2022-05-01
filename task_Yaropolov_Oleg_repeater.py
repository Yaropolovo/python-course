from contextlib import ContextDecorator
from functools import wraps

def verbose(function):
    """verbose realization"""
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("before function call")
        outcome = function(*args, **kwargs)
        print("after function call")
        return outcome
    return wrapper

def repeater(count: int):
    """repeater realization"""
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            for iteration in range(count):
                outcome = function(*args, **kwargs)
            return outcome
        return wrapper
    return decorator

class verbose_context(ContextDecorator):
    """verbose context realization"""
    def __enter__(self):
        print("class: before function call")
        return self
    def __exit__(self, *exc):
        print("class: after function call")
        return self
