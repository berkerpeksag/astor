# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2012 (c) Patrick Maupin
Copyright 2013 (c) Berker Peksag

"""

import ast
import sys


def parsefile(fname):
    with open(fname, 'r') as f:
        fstr = f.read()
    fstr = fstr.replace('\r\n', '\n').replace('\r', '\n')
    if not fstr.endswith('\n'):
        fstr += '\n'
    return ast.parse(fstr, filename=fname)


class CodeToAst(object):
    """Given a module, or a function that was compiled as part
    of a module, re-compile the module into an AST and extract
    the sub-AST for the function.  Allow caching to reduce
    number of compiles.

    """
    def __init__(self, cache=None):
        self.cache = cache or {}

    def __call__(self, codeobj):
        cache = self.cache
        fname = getattr(codeobj, '__file__', None)
        if fname is None:
            func_code = codeobj.__code__
            fname = func_code.co_filename
            linenum = func_code.co_firstlineno
            key = fname, linenum
        else:
            fname = key = fname.replace('.pyc', '.py')
        result = cache.get(key)
        if result is not None:
            return result
        cache[fname] = mod_ast = parsefile(fname)
        for obj in mod_ast.body:
            if not isinstance(obj, ast.FunctionDef):
                continue
            cache[(fname, obj.lineno)] = obj
        return cache[key]

codetoast = CodeToAst()
