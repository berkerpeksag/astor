"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright 2014 (c) Berker Peksag
"""

import ast
import sys
import textwrap

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


class CodegenTestCase(unittest.TestCase):

    def assertAstSourceEqual(self, source):
        self.assertEqual(astor.to_source(ast.parse(source)), source)

    def assertAstSourceEqualIfAtLeastVersion(self, source, version_tuple, version2=None):
        if version2 is None:
            version2 = version_tuple[0], version_tuple[1] - 1
        if sys.version_info >= version_tuple:
            self.assertAstSourceEqual(source)
        elif sys.version_info <= version2:
            self.assertRaises(SyntaxError, ast.parse, source)

    def test_imports(self):
        source = "import ast"
        self.assertAstSourceEqual(source)
        source = "import operator as op"
        self.assertAstSourceEqual(source)
        source = "from math import floor"
        self.assertAstSourceEqual(source)
        source = "from .. import foobar"
        self.assertAstSourceEqual(source)

    def test_dictionary_literals(self):
        source = "{'a': 1, 'b': 2}"
        self.assertAstSourceEqual(source)
        another_source = "{'nested': ['structures', {'are': 'important'}]}"
        self.assertAstSourceEqual(another_source)

    def test_try_expect(self):
        source = textwrap.dedent("""\
        try:
            'spam'[10]
        except IndexError:
            pass""")
        self.assertAstSourceEqual(source)

        source = textwrap.dedent("""\
        try:
            'spam'[10]
        except IndexError as exc:
            sys.stdout.write(exc)""")
        self.assertAstSourceEqual(source)

        source = textwrap.dedent("""\
        try:
            'spam'[10]
        except IndexError as exc:
            sys.stdout.write(exc)
        else:
            pass
        finally:
            pass""")
        # This is interesting -- the latest 2.7 compiler seems to
        # handle this OK, but creates an AST with nested try/finally
        # and try/except, so the source code doesn't match.
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 4), (1, 0))

    def test_del_statement(self):
        source = "del l[0]"
        self.assertAstSourceEqual(source)
        source = "del obj.x"
        self.assertAstSourceEqual(source)

    def test_arguments(self):
        source = textwrap.dedent("""\
        j = [1, 2, 3]

        def test(a1, a2, b1=j, b2='123', b3={}, b4=[]):
            pass""")
        self.assertAstSourceEqual(source)

    def test_pass_arguments_node(self):
        source = textwrap.dedent("""\
        j = [1, 2, 3]
        def test(a1, a2, b1=j, b2='123', b3={}, b4=[]):
            pass""")
        root_node = ast.parse(source)
        arguments_node = [n for n in ast.walk(root_node)
                          if isinstance(n, ast.arguments)][0]
        self.assertEqual(astor.to_source(arguments_node),
                         "a1, a2, b1=j, b2='123', b3={}, b4=[]")
        source = textwrap.dedent("""\
        def call(*popenargs, timeout=None, **kwargs):
            pass""")
        # Probably also works on < 3.4, but doesn't work on 2.7...
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 4), (2, 7))

    def test_matrix_multiplication(self):
        for source in ("(a @ b)", "a @= b"):
            self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_multiple_call_unpackings(self):
        source = textwrap.dedent("""\
        my_function(*[1], *[2], **{'three': 3}, **{'four': 'four'})""")
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_right_hand_side_dictionary_unpacking(self):
        source = textwrap.dedent("""\
        our_dict = {'a': 1, **{'b': 2, 'c': 3}}""")
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_async_def_with_for(self):
        source = textwrap.dedent("""\
        async def read_data(db):
            async with connect(db) as db_cxn:
                data = await db_cxn.fetch('SELECT foo FROM bar;')
            async for datum in data:
                if quux(datum):
                    return datum""")
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_class_definition_with_starbases_and_kwargs(self):
        source = textwrap.dedent("""\
        class TreeFactory(*[FactoryMixin, TreeBase], **{'metaclass': Foo}):
            pass""")
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 0))

    def test_yield(self):
        source = "yield"
        self.assertAstSourceEqual(source)
        source = textwrap.dedent("""\
        def dummy():
            yield""")
        self.assertAstSourceEqual(source)
        source = "foo((yield bar))"
        self.assertAstSourceEqual(source)
        source = "return (yield from sam())"
        # Probably also works on < 3.4, but doesn't work on 2.7...
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 4), (2, 7))
        
    def test_pretty_docstring(self):
        source = textwrap.dedent('''\
        def my_function():
            """
            docstring
            """
            return 1''')        
        self.assertAstSourceEqual(source)


if __name__ == '__main__':
    unittest.main()
