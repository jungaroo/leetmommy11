from functools import wraps

def deprecated(func):
    """Decorator to signify deprecated function. Will print out the docstring """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(func.__name__, " is deprecated.", func.__doc__)
        return func(*args, **kwargs)
    return wrapper