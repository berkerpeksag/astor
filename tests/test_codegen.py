"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright 2014 (c) Berker Peksag
"""

import ast
import unittest
import textwrap

import astor


class CodegenTestCase(unittest.TestCase):

    def assertAstSourceEqual(self, source):
        self.assertEqual(astor.to_source(ast.parse(source)), source)

    def test_imports(self):
        source = "import ast"
        self.assertAstSourceEqual(source)
        source = "import operator as op"
        self.assertAstSourceEqual(source)
        source = "from math import floor"
        self.assertAstSourceEqual(source)

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

    def test_del_statement(self):
        source = "del l[0]"
        self.assertAstSourceEqual(source)
        source = "del obj.x"
        self.assertAstSourceEqual(source)

    def test_arguments(self):
        source = textwrap.dedent("""\
        j=[1,2,3]
        def test(a1, a2, b1=j, b2='123', b3={}, b4=[]):
            pass""")
        root_node = ast.parse(source)
        arguments_node = [x for x in ast.walk(root_node) \
                                    if isinstance(x, ast.arguments)][0]
        self.assertEqual(astor.to_source(arguments_node), \
                        "a1, a2, b1=j, b2='123', b3={}, b4=[]")

if __name__ == '__main__':
    unittest.main()
