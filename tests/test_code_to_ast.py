import functools
import unittest

from astor import code_to_ast


def decorator(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def simple_decorator(f):
    f.__decorated__ = True
    return f


def undecorated_func():
    pass


@decorator
def decorated_func():
    pass


@decorator
@decorator
def twice_decorated_func():
    pass


@simple_decorator
def plain_decorated_func():
    pass


@simple_decorator
def simple_decorated_func():
    pass


@simple_decorator
@decorator
def twice_decorated_func_2():
    pass


class CodeToASTTestCase(unittest.TestCase):

    def test_decorated(self):
        self.assertIsNotNone(code_to_ast(decorated_func))

    def test_undecorated(self):
        self.assertIsNotNone(code_to_ast(undecorated_func))

    def test_twice_decorated(self):
        self.assertIsNotNone(code_to_ast(twice_decorated_func))

    def test_twice_decorated_2(self):
        self.assertIsNotNone(code_to_ast(twice_decorated_func_2))

    def test_plain_decorator(self):
        self.assertIsNotNone(code_to_ast(simple_decorated_func))

    def test_module(self):
        self.assertIsNotNone(code_to_ast(unittest))


if __name__ == '__main__':
    unittest.main()
