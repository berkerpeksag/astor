# coding: utf-8
"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright (c) 2014 Berker Peksag
Copyright (c) 2015 Patrick Maupin
"""

import ast
import math
import sys
import textwrap

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


def canonical(srctxt):
    return textwrap.dedent(srctxt).strip()

def astorexpr(x):
    return eval(astor.to_source(ast.Expression(body=x)))

def astornum(x):
    return astorexpr(ast.Num(n=x))

class Comparisons(object):

    to_source = staticmethod(astor.to_source)

    def assertAstEqual(self, ast1, ast2):
        dmp1 = astor.dump_tree(ast1)
        dmp2 = astor.dump_tree(ast2)
        self.assertEqual(dmp1, dmp2)

    def assertAstEqualsSource(self, tree, source):
        self.assertEqual(self.to_source(tree).rstrip(), source)

    def assertAstRoundtrips(self, srctxt):
        """This asserts that the reconstituted source
           code can be compiled into the exact same AST
           as the original source code.
        """
        srctxt = canonical(srctxt)
        srcast = ast.parse(srctxt)
        dsttxt = self.to_source(srcast)
        dstast = ast.parse(dsttxt)
        self.assertAstEqual(srcast, dstast)

    def assertAstRoundtripsGtVer(self, source, min_should_work,
                                 max_should_error=None):
        if max_should_error is None:
            max_should_error = min_should_work[0], min_should_work[1] - 1
        if sys.version_info >= min_should_work:
            self.assertAstRoundtrips(source)
        elif sys.version_info <= max_should_error:
            self.assertRaises(SyntaxError, ast.parse, source)

    def assertSrcRoundtrips(self, srctxt):
        """This asserts that the reconstituted source
           code is identical to the original source code.
           This is a much stronger statement than assertAstRoundtrips,
           which may not always be appropriate.
        """
        srctxt = canonical(srctxt)
        self.assertEqual(self.to_source(ast.parse(srctxt)).rstrip(), srctxt)

    def assertSrcDoesNotRoundtrip(self, srctxt):
        srctxt = canonical(srctxt)
        self.assertNotEqual(self.to_source(ast.parse(srctxt)).rstrip(),
                            srctxt)

    def assertSrcRoundtripsGtVer(self, source, min_should_work,
                                 max_should_error=None):
        if max_should_error is None:
            max_should_error = min_should_work[0], min_should_work[1] - 1
        if sys.version_info >= min_should_work:
            self.assertSrcRoundtrips(source)
        elif sys.version_info <= max_should_error:
            self.assertRaises(SyntaxError, ast.parse, source)


class CodegenTestCase(unittest.TestCase, Comparisons):

    def test_imports(self):
        source = "import ast"
        self.assertSrcRoundtrips(source)
        source = "import operator as op"
        self.assertSrcRoundtrips(source)
        source = "from math import floor"
        self.assertSrcRoundtrips(source)
        source = "from .. import foobar"
        self.assertSrcRoundtrips(source)
        source = "from ..aaa import foo, bar as bar2"
        self.assertSrcRoundtrips(source)

    def test_empty_iterable_literals(self):
        self.assertSrcRoundtrips('()')
        self.assertSrcRoundtrips('[]')
        self.assertSrcRoundtrips('{}')
        # Python has no literal for empty sets, but code_gen should produce an
        # expression that evaluates to one.
        self.assertEqual(astorexpr(ast.Set([])), set())

    def test_dictionary_literals(self):
        source = "{'a': 1, 'b': 2}"
        self.assertSrcRoundtrips(source)
        another_source = "{'nested': ['structures', {'are': 'important'}]}"
        self.assertSrcRoundtrips(another_source)

    def test_try_expect(self):
        source = """
            try:
                'spam'[10]
            except IndexError:
                pass"""
        self.assertAstRoundtrips(source)

        source = """
            try:
                'spam'[10]
            except IndexError as exc:
                sys.stdout.write(exc)"""
        self.assertAstRoundtrips(source)

        source = """
            try:
                'spam'[10]
            except IndexError as exc:
                sys.stdout.write(exc)
            else:
                pass
            finally:
                pass"""
        self.assertAstRoundtrips(source)
        source = """
            try:
                size = len(iterable)
            except (TypeError, AttributeError):
                pass
            else:
                if n >= size:
                    return sorted(iterable, key=key, reverse=True)[:n]"""
        self.assertAstRoundtrips(source)

    def test_del_statement(self):
        source = "del l[0]"
        self.assertSrcRoundtrips(source)
        source = "del obj.x"
        self.assertSrcRoundtrips(source)

    def test_arguments(self):
        source = """
            j = [1, 2, 3]


            def test(a1, a2, b1=j, b2='123', b3={}, b4=[]):
                pass"""
        self.assertSrcRoundtrips(source)

    @unittest.skipUnless(sys.version_info >= (3, 8, 0, "alpha", 4),
                         "positional only arguments introduced in Python 3.8")
    def test_positional_only_arguments(self):
        source = """
        def test(a, b, /, c, *, d, **kwargs):
            pass


        def test(a=3, b=4, /, c=7):
            pass


        def test(a, b=4, /, c=8, d=9):
            pass
        """
        self.assertSrcRoundtrips(source)

    def test_pass_arguments_node(self):
        source = canonical("""
            j = [1, 2, 3]


            def test(a1, a2, b1=j, b2='123', b3={}, b4=[]):
                pass""")
        root_node = ast.parse(source)
        arguments_node = [n for n in ast.walk(root_node)
                          if isinstance(n, ast.arguments)][0]
        self.assertEqual(self.to_source(arguments_node).rstrip(),
                         "a1, a2, b1=j, b2='123', b3={}, b4=[]")
        source = """
            def call(*popenargs, timeout=None, **kwargs):
                pass"""
        # Probably also works on < 3.4, but doesn't work on 2.7...
        self.assertSrcRoundtripsGtVer(source, (3, 4), (2, 7))

    def test_attribute(self):
        self.assertSrcRoundtrips("x.foo")
        self.assertSrcRoundtrips("(5).foo")

    def test_matrix_multiplication(self):
        for source in ("(a @ b)", "a @= b"):
            self.assertAstRoundtripsGtVer(source, (3, 5))

    def test_multiple_call_unpackings(self):
        source = """
            my_function(*[1], *[2], **{'three': 3}, **{'four': 'four'})"""
        self.assertSrcRoundtripsGtVer(source, (3, 5))

    def test_right_hand_side_dictionary_unpacking(self):
        source = """
            our_dict = {'a': 1, **{'b': 2, 'c': 3}}"""
        self.assertSrcRoundtripsGtVer(source, (3, 5))

    def test_async_def_with_for(self):
        source = """
            async def read_data(db):
                async with connect(db) as db_cxn:
                    data = await db_cxn.fetch('SELECT foo FROM bar;')
                async for datum in data:
                    if quux(datum):
                        return datum"""
        self.assertSrcRoundtripsGtVer(source, (3, 5))

    def test_double_await(self):
        source = """
            async def foo():
                return await (await bar())"""
        self.assertSrcRoundtripsGtVer(source, (3, 5))

    def test_class_definition_with_starbases_and_kwargs(self):
        source = """
            class TreeFactory(*[FactoryMixin, TreeBase], **{'metaclass': Foo}):
                pass"""
        self.assertSrcRoundtripsGtVer(source, (3, 0))

    def test_yield(self):
        source = "yield"
        self.assertAstRoundtrips(source)
        source = """
        def dummy():
            yield"""
        self.assertAstRoundtrips(source)
        source = "foo((yield bar))"
        self.assertAstRoundtrips(source)
        source = "(yield bar)()"
        self.assertAstRoundtrips(source)
        source = "return (yield 1)"
        self.assertAstRoundtrips(source)
        source = "return (yield from sam())"
        self.assertAstRoundtripsGtVer(source, (3, 3))
        source = "((yield a) for b in c)"
        self.assertAstRoundtrips(source)
        source = "[(yield)]"
        self.assertAstRoundtrips(source)
        source = "if (yield): pass"
        self.assertAstRoundtrips(source)
        source = "if (yield from foo): pass"
        self.assertAstRoundtripsGtVer(source, (3, 3))
        source = "(yield from (a, b))"
        self.assertAstRoundtripsGtVer(source, (3, 3))
        source = "yield from sam()"
        self.assertSrcRoundtripsGtVer(source, (3, 3))

    def test_with(self):
        source = """
            with foo:
                pass
        """
        self.assertSrcRoundtrips(source)
        source = """
            with foo as bar:
                pass
        """
        self.assertSrcRoundtrips(source)
        source = """
            with foo as bar, mary, william as bill:
                pass
        """
        self.assertAstRoundtripsGtVer(source, (2, 7))

    def test_huge_int(self):
        for n in (10**10000,
                  0xdfa21cd2a530ccc8c870aa60d9feb3b35deeab81c3215a96557abbd683d21f4600f38e475d87100da9a4404220eeb3bb5584e5a2b5b48ffda58530ea19104a32577d7459d91e76aa711b241050f4cc6d5327ccee254f371bcad3be56d46eb5919b73f20dbdb1177b700f00891c5bf4ed128bb90ed541b778288285bcfa28432ab5cbcb8321b6e24760e998e0daa519f093a631e44276d7dd252ce0c08c75e2ab28a7349ead779f97d0f20a6d413bf3623cd216dc35375f6366690bcc41e3b2d5465840ec7ee0dc7e3f1c101d674a0c7dbccbc3942788b111396add2f8153b46a0e4b50d66e57ee92958f1c860dd97cc0e40e32febff915343ed53573142bdf4b):
            self.assertEqual(astornum(n), n)

    def test_complex(self):
        source = """
            (3) + (4j) + (1+2j) + (1+0j)
        """
        self.assertAstRoundtrips(source)

        self.assertIsInstance(astornum(1+0j), complex)

    def test_inf(self):
        source = """
            (1e1000) + (-1e1000) + (1e1000j) + (-1e1000j)
        """
        self.assertAstRoundtrips(source)
        # We special case infinities in code_gen. So we will
        # return the same AST construction but it won't
        # roundtrip to 'source'. See the SourceGenerator.visit_Num
        # method for details. (#82)
        source = 'a = 1e400'
        self.assertAstRoundtrips(source)
        # Returns 'a = 1e1000'.
        self.assertSrcDoesNotRoundtrip(source)

        self.assertIsInstance(astornum((1e1000+1e1000)+0j), complex)

    def test_nan(self):
        self.assertTrue(math.isnan(astornum(float('nan'))))

        v = astornum(complex(-1e1000, float('nan')))
        self.assertEqual(v.real, -1e1000)
        self.assertTrue(math.isnan(v.imag))

        v = astornum(complex(float('nan'), -1e1000))
        self.assertTrue(math.isnan(v.real))
        self.assertEqual(v.imag, -1e1000)

    def test_unary(self):
        source = """
            -(1) + ~(2) + +(3)
        """
        self.assertAstRoundtrips(source)

    def test_pow(self):
        source = """
            (-2) ** (-3)
        """
        self.assertAstRoundtrips(source)
        source = """
            (+2) ** (+3)
        """
        self.assertAstRoundtrips(source)
        source = """
            2 ** 3 ** 4
        """
        self.assertAstRoundtrips(source)
        source = """
            -2 ** -3
        """
        self.assertAstRoundtrips(source)
        source = """
            -2 ** -3 ** -4
        """
        self.assertAstRoundtrips(source)
        source = """
            -((-1) ** other._sign)
            (-1) ** self._sign
        """
        self.assertAstRoundtrips(source)

    def test_comprehension(self):
        source = """
            ((x,y) for x,y in zip(a,b) if a)
        """
        self.assertAstRoundtrips(source)
        source = """
            fields = [(a, _format(b)) for (a, b) in iter_fields(node) if a]
        """
        self.assertAstRoundtrips(source)
        source = """
            ra = np.fromiter(((i * 3, i * 2) for i in range(10)),
                                n, dtype='i8,f8')
        """
        self.assertAstRoundtrips(source)

    def test_async_comprehension(self):
        source = """
            async def f():
                [(await x) async for x in y]
                [(await i) for i in b if await c]
                (await x async for x in y)
                {i for i in b async for i in a if await i for b in i}
        """
        self.assertSrcRoundtripsGtVer(source, (3, 6))

    def test_tuple_corner_cases(self):
        source = """
            a = ()
        """
        self.assertAstRoundtrips(source)
        source = """
            assert (a, b), (c, d)
        """
        self.assertAstRoundtrips(source)
        source = """
            return UUID(fields=(time_low, time_mid, time_hi_version,
                  clock_seq_hi_variant, clock_seq_low, node), version=1)
        """
        self.assertAstRoundtrips(source)
        source = """
            raise(os.error, ('multiple errors:', errors))
        """
        self.assertAstRoundtrips(source)
        source = """
            exec(expr, global_dict, local_dict)
        """
        self.assertAstRoundtrips(source)
        source = """
            with (a, b) as (c, d):
                pass
        """
        self.assertAstRoundtrips(source)
        self.assertAstRoundtrips(source)
        source = """
            with (a, b) as (c, d), (e,f) as (h,g):
                pass
        """
        self.assertAstRoundtripsGtVer(source, (2, 7))
        source = """
            Pxx[..., (0,-1)] = xft[..., (0,-1)]**2
        """
        self.assertAstRoundtripsGtVer(source, (2, 7))
        source = """
            responses = {
                v: (v.phrase, v.description)
                for v in HTTPStatus.__members__.values()
            }
        """
        self.assertAstRoundtripsGtVer(source, (2, 7))

    def test_output_formatting(self):
        source = """
            __all__ = ['ArgumentParser', 'ArgumentError', 'ArgumentTypeError',
                'FileType', 'HelpFormatter', 'ArgumentDefaultsHelpFormatter',
                'RawDescriptionHelpFormatter', 'RawTextHelpFormatter', 'Namespace',
                'Action', 'ONE_OR_MORE', 'OPTIONAL', 'PARSER', 'REMAINDER', 'SUPPRESS',
                'ZERO_OR_MORE']
        """  # NOQA
        self.maxDiff = 2000
        self.assertSrcRoundtrips(source)

    def test_elif(self):
        source = """
            if a:
                b
            elif c:
                d
            elif e:
                f
            else:
                g
        """
        self.assertSrcRoundtrips(source)

    def test_fstrings(self):
        source = """
        x = f'{x}'
        x = f'{x.y}'
        x = f'{int(x)}'
        x = f'a{b:c}d'
        x = f'a{b!s:c{d}e}f'
        x = f'{x + y}'
        x = f'""'
        x = f'"\\''
        """
        self.assertSrcRoundtripsGtVer(source, (3, 6))
        source = """
        a_really_long_line_will_probably_break_things = (
            f'a{b!s:c{d}e}fghijka{b!s:c{d}e}a{b!s:c{d}e}a{b!s:c{d}e}')
        """
        self.assertSrcRoundtripsGtVer(source, (3, 6))
        source = """
        return f"functools.{qualname}({', '.join(args)})"
        """
        self.assertSrcRoundtripsGtVer(source, (3, 6))

    def test_assignment_expr(self):
        cases = (
            "(x := 3)",
            "1 + (x := y)",
            "x = (y := 0)",
            "1 + (p := 1 if 2 else 3)",
            "[y := f(x), y**2, y**3]",
            "(2 ** 3 * 4 + 5 and 6, x := 2 ** 3 * 4 + 5 and 6)",
            "foo(x := 3, cat='vector')",
            "foo(x=(y := f(x)))",
            "any(len(longline := line) >= 100 for line in lines)",
            "[[y := f(x), x/y] for x in range(5)]",
            "lambda: (x := 1)",
            "def foo(answer=(p := 42)): pass",
            "def foo(answer: (p := 42) = 5): pass",
            "if reductor := dispatch_table.get(cls): pass",
            "while line := fp.readline(): pass",
            "while (command := input('> ')) != 'quit': pass")
        for case in cases:
            self.assertAstRoundtripsGtVer(case, (3, 8))

    @unittest.skipUnless(sys.version_info <= (3, 3),
                         "ast.Name used for True, False, None until Python 3.4")
    def test_deprecated_constants_as_name(self):
        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Name(id='True')),
            "spam = True")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Name(id='False')),
            "spam = False")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Name(id='None')),
            "spam = None")

    @unittest.skipUnless(sys.version_info >= (3, 4),
                         "ast.NameConstant introduced in Python 3.4")
    def test_deprecated_name_constants(self):
        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.NameConstant(value=True)),
            "spam = True")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.NameConstant(value=False)),
            "spam = False")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.NameConstant(value=None)),
            "spam = None")

    def test_deprecated_constant_nodes(self):
        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Num(3)),
            "spam = 3")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Num(-93)),
            "spam = -93")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Num(837.3888)),
            "spam = 837.3888")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Num(-0.9877)),
            "spam = -0.9877")

        self.assertAstEqualsSource(ast.Ellipsis(), "...")

        if sys.version_info >= (3, 0):
            self.assertAstEqualsSource(
                ast.Assign(targets=[ast.Name(id='spam')], value=ast.Bytes(b"Bytes")),
                "spam = b'Bytes'")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Str("String")),
            "spam = 'String'")

    @unittest.skipUnless(sys.version_info >= (3, 6),
                         "ast.Constant introduced in Python 3.6")
    def test_constant_nodes(self):
        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value=3)),
            "spam = 3")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value=-93)),
            "spam = -93")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value=837.3888)),
            "spam = 837.3888")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value=-0.9877)),
            "spam = -0.9877")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value=True)),
            "spam = True")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value=False)),
            "spam = False")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value=None)),
            "spam = None")

        self.assertAstEqualsSource(ast.Constant(value=Ellipsis), "...")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(b"Bytes")),
            "spam = b'Bytes'")

        self.assertAstEqualsSource(
            ast.Assign(targets=[ast.Name(id='spam')], value=ast.Constant(value="String")),
            "spam = 'String'")

    def test_annassign(self):
        source = """
            a: int
            (a): int
            a.b: int
            (a.b): int
            b: Tuple[int, str, ...]
            c.d[e].f: Any
            q: 3 = (1, 2, 3)
            t: Tuple[int, ...] = (1, 2, 3)
            some_list: List[int] = []
            (a): int = 0
            a:int = 0
            (a.b): int = 0
            a.b: int = 0
        """
        self.assertAstRoundtripsGtVer(source, (3, 6))

    @unittest.skipUnless(sys.version_info >= (3, 6),
                         "typing and annotated assignment was introduced in "
                         "Python 3.6")
    def test_function_typing(self):
        source = canonical("""
        def foo(x : int) ->str:
            i : str = '3'
            return i
        """)
        target = canonical("""
        def foo(x: int) -> str:
            i: str = '3'
            return i
        """)
        self.assertAstEqualsSource(ast.parse(source), target)

    def test_compile_types(self):
        code = '(a + b + c) * (d + e + f)\n'
        for mode in 'exec eval single'.split():
            srcast = compile(code, 'dummy', mode, ast.PyCF_ONLY_AST)
            dsttxt = self.to_source(srcast)
            if code.strip() != dsttxt.strip():
                self.assertEqual('(%s)' % code.strip(), dsttxt.strip())

    def test_unicode_literals(self):
        source = """
        from __future__ import (print_function, unicode_literals)
        x = b'abc'
        y = u'abc'
        """
        self.assertAstRoundtrips(source)

    def test_slicing(self):
        source = """
            x[1,2]
            x[...,...]
            x[1,...]
            x[...,3]
            x[:,:]
            x[:,]
            x[1,:]
            x[:,2]
            x[1:2,]
            x[3:4,...]
            x[5:6,7:8]
            x[1:2,3:4]
            x[5:6:7,]
            x[1:2:-3,]
            x[4:5:6,...]
            x[7:8:-9,...]
            x[1:2:3,4:5]
            x[6:7:-8,9:0]
            x[...,1:2]
            x[1:2,3:4]
            x[...,1:2:3]
            x[...,4:5:-6]
            x[1:2,3:4:5]
            x[1:2,3:4:-5]
        """
        self.assertAstRoundtrips(source)

    def test_non_string_leakage(self):
        source = '''
        tar_compression = {'gzip': 'gz', None: ''}
        '''
        self.assertAstRoundtrips(source)

    def test_fstring_trailing_newline(self):
        source = '''
        x = f"""{host}\n\t{port}\n"""
        '''
        self.assertSrcRoundtripsGtVer(source, (3, 6))
        source = '''
        if 1:
            x = f'{host}\\n\\t{port}\\n'
        '''
        self.assertSrcRoundtripsGtVer(source, (3, 6))

    def test_fstring_escaped_braces(self):
        source = '''
        x = f'{{hello world}}'
        '''
        self.assertSrcRoundtripsGtVer(source, (3, 6))
        source = '''
        x = f'{f.name}={{self.{f.name}!r}}'
        '''
        self.assertSrcRoundtripsGtVer(source, (3, 6))

    @unittest.skipUnless(sys.version_info >= (3, 8, 0, "alpha", 4),
                         "f-string debugging introduced in Python 3.8")
    def test_fstring_debugging(self):
        source = """
        x = f'{5=}'
        y = f'{5=!r}'
        z = f'{3*x+15=}'
        f'{x=:}'
        f'{x=:.2f}'
        f'alpha α {pi=} ω omega'
        """
        self.assertAstRoundtripsGtVer(source, (3, 8))

    def test_docstring_function(self):
        source = '''
        def f(arg):
            """
            docstring
            """
            return 3
        '''
        self.assertSrcRoundtrips(source)

    def test_docstring_class(self):
        source = '''
        class Class:
            """
            docstring
            """
            pass
        '''
        self.assertSrcRoundtrips(source)

    def test_docstring_method(self):
        source = '''
        class Class:

            def f(arg):
                """
                docstring
                """
                return 3
        '''
        self.assertSrcRoundtrips(source)

    def test_docstring_module(self):
        source = '''
        """
        docstring1
        """


        class Class:

            def f(arg):
                pass
        '''
        self.assertSrcRoundtrips(source)


if __name__ == '__main__':
    unittest.main()
