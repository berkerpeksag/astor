import ast

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from . import test_code_gen

import astunparse


class MyTests(test_code_gen.CodegenTestCase):
    to_source = staticmethod(astunparse.unparse)

    # Just see if it'll do anything good at all
    assertSrcRoundtrips = test_code_gen.CodegenTestCase.assertAstRoundtrips

    # Don't look for exact comparison; see if ASTs match
    def assertSrcEqual(self, src1, src2):
        self.assertAstEqual(ast.parse(src1), ast.parse(src2))


if __name__ == '__main__':
    unittest.main()
