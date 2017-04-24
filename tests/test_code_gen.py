"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright (c) 2014 Berker Peksag
Copyright (c) 2015 Patrick Maupin
"""

import ast
import sys
import textwrap

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


def canonical(srctxt):
    return textwrap.dedent(srctxt).strip()


class CodegenTestCase(unittest.TestCase):

    def assertAstEqual(self, srctxt):
        """This asserts that the reconstituted source
           code can be compiled into the exact same AST
           as the original source code.
        """
        srctxt = canonical(srctxt)
        srcast = ast.parse(srctxt)
        dsttxt = astor.to_source(srcast)
        dstast = ast.parse(dsttxt)
        srcdmp = astor.dump_tree(srcast)
        dstdmp = astor.dump_tree(dstast)
        self.assertEqual(dstdmp, srcdmp)

    def assertAstEqualIfAtLeastVersion(self, source, min_should_work,
                                       max_should_error=None):
        if max_should_error is None:
            max_should_error = min_should_work[0], min_should_work[1] - 1
        if sys.version_info >= min_should_work:
            self.assertAstEqual(source)
        elif sys.version_info <= max_should_error:
            self.assertRaises(SyntaxError, ast.parse, source)

    def assertAstSourceEqual(self, srctxt):
        """This asserts that the reconstituted source
           code is identical to the original source code.
           This is a much stronger statement than assertAstEqual,
           which may not always be appropriate.
        """
        srctxt = canonical(srctxt)
        self.assertEqual(astor.to_source(ast.parse(srctxt)).rstrip(), srctxt)

    def assertAstSourceEqualIfAtLeastVersion(self, source, min_should_work,
                                             max_should_error=None):
        if max_should_error is None:
            max_should_error = min_should_work[0], min_should_work[1] - 1
        if sys.version_info >= min_should_work:
            self.assertAstSourceEqual(source)
        elif sys.version_info <= max_should_error:
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
        source = "from ..aaa import foo, bar as bar2"
        self.assertAstSourceEqual(source)

    def test_dictionary_literals(self):
        source = "{'a': 1, 'b': 2}"
        self.assertAstSourceEqual(source)
        another_source = "{'nested': ['structures', {'are': 'important'}]}"
        self.assertAstSourceEqual(another_source)

    def test_try_expect(self):
        source = """
            try:
                'spam'[10]
            except IndexError:
                pass"""
        self.assertAstEqual(source)

        source = """
            try:
                'spam'[10]
            except IndexError as exc:
                sys.stdout.write(exc)"""
        self.assertAstEqual(source)

        source = """
            try:
                'spam'[10]
            except IndexError as exc:
                sys.stdout.write(exc)
            else:
                pass
            finally:
                pass"""
        self.assertAstEqual(source)
        source = """
            try:
                size = len(iterable)
            except (TypeError, AttributeError):
                pass
            else:
                if n >= size:
                    return sorted(iterable, key=key, reverse=True)[:n]"""
        self.assertAstEqual(source)

    def test_del_statement(self):
        source = "del l[0]"
        self.assertAstSourceEqual(source)
        source = "del obj.x"
        self.assertAstSourceEqual(source)

    def test_arguments(self):
        source = """
            j = [1, 2, 3]

            def test(a1, a2, b1=j, b2='123', b3={}, b4=[]):
                pass"""
        self.assertAstSourceEqual(source)

    def test_pass_arguments_node(self):
        source = canonical("""
            j = [1, 2, 3]

            def test(a1, a2, b1=j, b2='123', b3={}, b4=[]):
                pass""")
        root_node = ast.parse(source)
        arguments_node = [n for n in ast.walk(root_node)
                          if isinstance(n, ast.arguments)][0]
        self.assertEqual(astor.to_source(arguments_node).rstrip(),
                         "a1, a2, b1=j, b2='123', b3={}, b4=[]")
        source = """
            def call(*popenargs, timeout=None, **kwargs):
                pass"""
        # Probably also works on < 3.4, but doesn't work on 2.7...
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 4), (2, 7))

    def test_matrix_multiplication(self):
        for source in ("(a @ b)", "a @= b"):
            self.assertAstEqualIfAtLeastVersion(source, (3, 5))

    def test_multiple_call_unpackings(self):
        source = """
            my_function(*[1], *[2], **{'three': 3}, **{'four': 'four'})"""
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_right_hand_side_dictionary_unpacking(self):
        source = """
            our_dict = {'a': 1, **{'b': 2, 'c': 3}}"""
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_async_def_with_for(self):
        source = """
            async def read_data(db):
                async with connect(db) as db_cxn:
                    data = await db_cxn.fetch('SELECT foo FROM bar;')
                async for datum in data:
                    if quux(datum):
                        return datum"""
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_double_await(self):
        source = """
            async def foo():
                return await (await bar())"""
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 5))

    def test_class_definition_with_starbases_and_kwargs(self):
        source = """
            class TreeFactory(*[FactoryMixin, TreeBase], **{'metaclass': Foo}):
                pass"""
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 0))

    def test_yield(self):
        source = "yield"
        self.assertAstEqual(source)
        source = """
        def dummy():
            yield"""
        self.assertAstEqual(source)
        source = "foo((yield bar))"
        self.assertAstEqual(source)
        source = "(yield bar)()"
        self.assertAstEqual(source)
        source = "return (yield 1)"
        self.assertAstEqual(source)
        source = "return (yield from sam())"
        self.assertAstEqualIfAtLeastVersion(source, (3, 3))
        source = "((yield a) for b in c)"
        self.assertAstEqual(source)
        source = "[(yield)]"
        self.assertAstEqual(source)
        source = "if (yield): pass"
        self.assertAstEqual(source)
        source = "if (yield from foo): pass"
        self.assertAstEqualIfAtLeastVersion(source, (3, 3))
        source = "(yield from (a, b))"
        self.assertAstEqualIfAtLeastVersion(source, (3, 3))
        source = "yield from sam()"
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 3))

    def test_with(self):
        source = """
            with foo:
                pass
        """
        self.assertAstSourceEqual(source)
        source = """
            with foo as bar:
                pass
        """
        self.assertAstSourceEqual(source)
        source = """
            with foo as bar, mary, william as bill:
                pass
        """
        self.assertAstEqualIfAtLeastVersion(source, (2, 7))

    def test_inf(self):
        source = """
            (1e1000) + (-1e1000) + (1e1000j) + (-1e1000j)
        """
        self.assertAstEqual(source)

    def test_unary(self):
        source = """
            -(1) + ~(2) + +(3)
        """
        self.assertAstEqual(source)

    def test_pow(self):
        source = """
            (-2) ** (-3)
        """
        self.assertAstEqual(source)
        source = """
            (+2) ** (+3)
        """
        self.assertAstEqual(source)
        source = """
            2 ** 3 ** 4
        """
        self.assertAstEqual(source)
        source = """
            -2 ** -3
        """
        self.assertAstEqual(source)
        source = """
            -2 ** -3 ** -4
        """
        self.assertAstEqual(source)
        source = """
            -((-1) ** other._sign)
            (-1) ** self._sign
        """
        self.assertAstEqual(source)

    def test_comprehension(self):
        source = """
            ((x,y) for x,y in zip(a,b) if a)
        """
        self.assertAstEqual(source)
        source = """
            fields = [(a, _format(b)) for (a, b) in iter_fields(node) if a]
        """
        self.assertAstEqual(source)
        source = """
            ra = np.fromiter(((i * 3, i * 2) for i in range(10)),
                                n, dtype='i8,f8')
        """
        self.assertAstEqual(source)

    def test_async_comprehension(self):
        source = """
            async def f():
                [(await x) async for x in y]
                [(await i) for i in b if await c]
                (await x async for x in y)
                {i for i in b async for i in a if await i for b in i}
        """
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 6))

    def test_tuple_corner_cases(self):
        source = """
            a = ()
        """
        self.assertAstEqual(source)
        source = """
            assert (a, b), (c, d)
        """
        self.assertAstEqual(source)
        source = """
            return UUID(fields=(time_low, time_mid, time_hi_version,
                  clock_seq_hi_variant, clock_seq_low, node), version=1)
        """
        self.assertAstEqual(source)
        source = """
            raise(os.error, ('multiple errors:', errors))
        """
        self.assertAstEqual(source)
        source = """
            exec(expr, global_dict, local_dict)
        """
        self.assertAstEqual(source)
        source = """
            with (a, b) as (c, d):
                pass
        """
        self.assertAstEqual(source)
        self.assertAstEqual(source)
        source = """
            with (a, b) as (c, d), (e,f) as (h,g):
                pass
        """
        self.assertAstEqualIfAtLeastVersion(source, (2, 7))
        source = """
            Pxx[..., (0,-1)] = xft[..., (0,-1)]**2
        """
        self.assertAstEqualIfAtLeastVersion(source, (2, 7))
        source = """
            responses = {
                v: (v.phrase, v.description)
                for v in HTTPStatus.__members__.values()
            }
        """
        self.assertAstEqualIfAtLeastVersion(source, (2, 7))

    def test_output_formatting(self):
        source = """
            __all__ = ['ArgumentParser', 'ArgumentError', 'ArgumentTypeError',
                'FileType', 'HelpFormatter', 'ArgumentDefaultsHelpFormatter',
                'RawDescriptionHelpFormatter', 'RawTextHelpFormatter', 'Namespace',
                'Action', 'ONE_OR_MORE', 'OPTIONAL', 'PARSER', 'REMAINDER', 'SUPPRESS',
                'ZERO_OR_MORE']
        """
        self.maxDiff=2000
        self.assertAstSourceEqual(source)

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
        self.assertAstSourceEqual(source)

    def test_fstrings(self):
        source = """
        f'{x}'
        f'{x.y}'
        f'{int(x)}'
        f'a{b:c}d'
        f'a{b!s:c{d}e}f'
        f'""'
        f'"\\''
        """
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 6))
        source = """
        a_really_long_line_will_probably_break_things = (
            f'a{b!s:c{d}e}fghijka{b!s:c{d}e}a{b!s:c{d}e}a{b!s:c{d}e}')
        """
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 6))
        source = """
        return f"functools.{qualname}({', '.join(args)})"
        """
        self.assertAstSourceEqualIfAtLeastVersion(source, (3, 6))


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
        self.assertAstEqualIfAtLeastVersion(source, (3, 6))


    def test_compile_types(self):
        code = '(a + b + c) * (d + e + f)\n'
        for mode in 'exec eval single'.split():
            srcast = compile(code, 'dummy', mode, ast.PyCF_ONLY_AST)
            dsttxt = astor.to_source(srcast)
            if code.strip() != dsttxt.strip():
                self.assertEqual('(%s)' % code.strip(), dsttxt.strip())

    def test_deprecation(self):
        ast1 = astor.code_to_ast.parse_file(__file__)
        src1 = astor.to_source(ast1)
        with self.assertWarns(DeprecationWarning):
            ast2 = astor.parsefile(__file__)
        with self.assertWarns(DeprecationWarning):
            src2 = astor.codegen.to_source(ast2)
        self.assertEqual(src1, src2)

    def test_unicode_literals(self):
        source = """
        from __future__ import (print_function, unicode_literals)
        x = b'abc'
        y = u'abc'
        """
        self.assertAstEqual(source)

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
        self.assertAstEqual(source)


if __name__ == '__main__':
    unittest.main()
