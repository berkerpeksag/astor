try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


class DummyClass:

    def __init__(self):
        self.x = 0

    def foo(self):

        def bar():
            return self.x

        return bar


class NestedFunctionTestCase(unittest.TestCase):

    def test_can_locate_method(self):
        dummy = DummyClass()
        _ = astor.code_to_ast(dummy.__init__)
        _ = astor.code_to_ast(dummy.foo())

