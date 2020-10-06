import ast
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


class OptionalAttributesTestCase(unittest.TestCase):

    def test_ImportFrom(self):
        """ Check ImportFrom node without 'module' and 'level' attributes """
        tree = ast.ImportFrom(
            names=[ast.alias(name='math', asname=None)],
        )
        self.assertIsInstance(astor.to_source(tree), str)

    def test_alias(self):
        """ Check alias node without 'asname' attribute """
        tree = ast.alias(name='math')
        self.assertIsInstance(astor.to_source(tree), str)


if __name__ == '__main__':
    unittest.main()
