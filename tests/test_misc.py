import ast
import sys
import warnings
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


class PublicAPITestCase(unittest.TestCase):

    def test_aliases(self):
        self.assertIs(astor.parse_file, astor.code_to_ast.parse_file)


class DeprecationTestCase(unittest.TestCase):

    def test_deprecate_parsefile(self):
        with self.assertWarns(DeprecationWarning):
            astor.parsefile(__file__)

    def test_deprecate_astor_codegen(self):
        with self.assertWarns(DeprecationWarning):
            import astor.codegen


class FastCompareTestCase(unittest.TestCase):

    def test_fast_compare(self):
        fast_compare = astor.node_util.fast_compare

        def check(a, b):
            ast_a = ast.parse(a)
            ast_b = ast.parse(b)
            dump_a = astor.dump_tree(ast_a)
            dump_b = astor.dump_tree(ast_b)
            self.assertEqual(dump_a == dump_b, fast_compare(ast_a, ast_b))
        check('a = 3', 'a = 3')
        check('a = 3', 'a = 5')
        check('a = 3 - (3, 4, 5)', 'a = 3 - (3, 4, 5)')
        check('a = 3 - (3, 4, 5)', 'a = 3 - (3, 4, 6)')


if __name__ == '__main__':
    unittest.main()
