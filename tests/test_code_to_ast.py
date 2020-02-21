from astor import code_to_ast
from functools import wraps

def example_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

@example_decorator
def example_decorated_func():
    pass

def example_undecorated_func():
    pass

@example_decorator
@example_decorator
def twice_decorated_func():
    pass

def test_code_to_ast():
    # validate we can get the ast for a decorated function
    ast = code_to_ast(example_decorated_func)
    assert ast is not None

    # validate we can get the ast for an undecorated function
    ast = code_to_ast(example_undecorated_func)
    assert ast is not None

    # validate we can get the ast for a multiply decorated function
    ast = code_to_ast(twice_decorated_func)
    assert ast is not None
