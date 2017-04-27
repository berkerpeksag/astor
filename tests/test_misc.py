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


class DeprecationTestCase(unittest.TestCase):

    def test_deprecation(self):
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            ast1 = astor.code_to_ast.parse_file(__file__)
            src1 = astor.to_source(ast1)
            ast2 = astor.parsefile(__file__)
            src2 = astor.codegen.to_source(ast2)
            self.assertEqual(len(w), 2)
            w = [warnings.formatwarning(x.message, x.category,
                                        x.filename, x.lineno) for x in w]
            w = [x.rsplit(':', 1)[-1].strip() for x in w]
            self.assertEqual(w[0], 'astor.parsefile is deprecated.  '
                             'Please use astor.code_to_ast.parse_file.\n'
                             '  ast2 = astor.parsefile(__file__)')
            self.assertEqual(w[1], 'astor.codegen is deprecated.  '
                             'Please use astor.code_gen.\n'
                             '  src2 = astor.codegen.to_source(ast2)')

        self.assertEqual(src1, src2)


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
