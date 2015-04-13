import ast
import unittest
import sys

import astor


class GetSymbolTestCase(unittest.TestCase):

    def test_get_mat_mult(self):
        if sys.version_info < (2, 7):
            # We can't use `@unittest.skipIf` or `raise skipTest` in
            # Python 2.6
            pass
        elif sys.version_info < (3, 5):
            raise unittest.SkipTest("ast.MatMult introduced in Python 3.5")
        else:
            self.assertEqual('@', astor.misc.get_binop(ast.MatMult()))


if __name__ == '__main__':
    unittest.main()
