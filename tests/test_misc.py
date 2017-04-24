import ast
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


class GetSymbolTestCase(unittest.TestCase):

    @unittest.skipUnless(sys.version_info >= (3, 5),
                         "ast.MatMult introduced in Python 3.5")
    def test_get_mat_mult(self):
        self.assertEqual('@', astor.get_op_symbol(ast.MatMult()))


if __name__ == '__main__':
    unittest.main()
