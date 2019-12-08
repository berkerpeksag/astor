import ast
import sys
import warnings
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor

from astor.source_repr import split_lines

from .support import import_fresh_module


class GetSymbolTestCase(unittest.TestCase):

    @unittest.skipUnless(sys.version_info >= (3, 5),
                         "ast.MatMult introduced in Python 3.5")
    def test_get_mat_mult(self):
        self.assertEqual('@', astor.get_op_symbol(ast.MatMult()))


class PublicAPITestCase(unittest.TestCase):

    def test_aliases(self):
        self.assertIs(astor.parse_file, astor.code_to_ast.parse_file)

    def test_codegen_from_root(self):
        with self.assertWarns(DeprecationWarning) as cm:
            astor = import_fresh_module('astor')
            astor.codegen.SourceGenerator
        self.assertEqual(len(cm.warnings), 1)
        # This message comes from 'astor/__init__.py'.
        self.assertEqual(
            str(cm.warning),
            'astor.codegen is deprecated.  Please use astor.code_gen.'
        )

    def test_codegen_as_submodule(self):
        with self.assertWarns(DeprecationWarning) as cm:
            import astor.codegen
        self.assertEqual(len(cm.warnings), 1)
        # This message comes from 'astor/codegen.py'.
        self.assertEqual(
            str(cm.warning),
            'astor.codegen module is deprecated. Please import '
            'astor.code_gen module instead.'
        )

    def test_to_source_invalid_customize_generator(self):
        class InvalidGenerator:
            pass

        node = ast.parse('spam = 42')

        with self.assertRaises(TypeError) as cm:
            astor.to_source(node, source_generator_class=InvalidGenerator)
        self.assertEqual(
            str(cm.exception),
            'source_generator_class should be a subclass of SourceGenerator',
        )

        with self.assertRaises(TypeError) as cm:
            astor.to_source(
                node,
                source_generator_class=astor.SourceGenerator(indent_with=' ' * 4),
            )
        self.assertEqual(
            str(cm.exception),
            'source_generator_class should be a class',
        )


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


class TreeWalkTestCase(unittest.TestCase):

    def test_auto_generated_attributes(self):
        # See #136 for more details.
        treewalk = astor.TreeWalk()
        self.assertIsInstance(treewalk.__dict__, dict)
        # Check that the inital state of the instance is empty.
        self.assertEqual(treewalk.__dict__['nodestack'], [])
        self.assertEqual(treewalk.__dict__['pre_handlers'], {})
        self.assertEqual(treewalk.__dict__['post_handlers'], {})


class SourceReprTestCase(unittest.TestCase):
    """
    Tests for helpers in astor.source_repr module.

    Note that these APIs are not public.
    """

    @unittest.skipUnless(sys.version_info[0] == 2, 'only applies to Python 2')
    def test_split_lines_unicode_support(self):
        source = [u'copy', '\n']
        self.assertEqual(split_lines(source), source)


if __name__ == '__main__':
    unittest.main()
