# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2012 (c) Patrick Maupin
Copyright 2013 (c) Berker Peksag

"""

import ast
import sys
import os


class NonExistent(object):
    pass


def iter_node(node, name='', list=list, getattr=getattr, isinstance=isinstance,
              enumerate=enumerate, missing=NonExistent):
    """Iterates over an object:

       - If the object has a _fields attribute,
         it gets attributes in the order of this
         and returns name, value pairs.

       - Otherwise, if the object is a list instance,
         it returns name, value pairs for each item
         in the list, where the name is passed into
         this function (defaults to blank).

    """
    fields = getattr(node, '_fields', None)
    if fields is not None:
        for name in fields:
            value = getattr(node, name, missing)
            if value is not missing:
                yield value, name
    elif isinstance(node, list):
        for value in node:
            yield value, name


def dump(node, name=None, initial_indent='', indentation='    ',
         maxline=120, maxmerged=80, iter_node=iter_node, special=ast.AST,
         list=list, isinstance=isinstance, type=type, len=len):
    """Dumps an AST or similar structure:

       - Pretty-prints with indentation
       - Doesn't print line/column/ctx info

    """
    def dump(node, name=None, indent=''):
        level = indent + indentation
        name = name and name + '=' or ''
        values = list(iter_node(node))
        if isinstance(node, list):
            prefix, suffix = '%s[' % name, ']'
        elif values:
            prefix, suffix = '%s%s(' % (name, type(node).__name__), ')'
        elif isinstance(node, special):
            prefix, suffix = name + type(node).__name__, ''
        else:
            return '%s%s' % (name, repr(node))
        node = [dump(a, b, level) for a, b in values if b != 'ctx']
        oneline = '%s%s%s' % (prefix, ', '.join(node), suffix)
        if len(oneline) + len(indent) < maxline:
            return '%s' % oneline
        if node and len(prefix) + len(node[0]) < maxmerged:
            prefix = '%s%s,' % (prefix, node.pop(0))
        node = (',\n%s' % level).join(node).lstrip()
        return '%s\n%s%s%s' % (prefix, level, node, suffix)
    return dump(node, name, initial_indent)


class MetaFlatten(type):
    """This metaclass is used to flatten classes to remove
    class hierarchy.

    This makes it easier to manipulate classes (find
    attributes in a single dict, etc.)

    """
    def __new__(clstype, name, bases, clsdict):
        newbases = (object,)
        newdict = {}
        for base in reversed(bases):
            if base not in newbases:
                newdict.update(vars(base))
        newdict.update(clsdict)
        # Delegate the real work to type
        return type.__new__(clstype, name, newbases, newdict)

MetaFlatten = MetaFlatten('MetaFlatten', (object, ), {})


def _getsymbol(mapping, map_dict=None, type=type):
    """This function returns a closure that will map a
    class type to its corresponding symbol, by looking
    up the class name of an object.

    """
    if isinstance(mapping, str):
        mapping = mapping.split()
        mapping = list(zip(mapping[0::2],
                           (x.replace('_', ' ') for x in mapping[1::2])))
        mapping = dict(((getattr(ast, x), y) for x, y in mapping))
    if map_dict is not None:
        map_dict.update(mapping)

    def getsymbol(obj, fmt='%s'):
        return fmt % mapping[type(obj)]
    return getsymbol

all_symbols = {}

get_boolop = _getsymbol("""
    And and   Or or
""", all_symbols)

binops = """
    Add +   Mult *   LShift <<   BitAnd &
    Sub -   Div  /   RShift >>   BitOr  |
            Mod  %               BitXor ^
            FloorDiv //
            Pow **
"""
if sys.version_info >= (3, 5):
    binops += "MatMult @"


get_binop = _getsymbol(binops, all_symbols)

get_cmpop = _getsymbol("""
  Eq    ==   Gt >   GtE >=   In    in       Is    is
  NotEq !=   Lt <   LtE <=   NotIn not_in   IsNot is_not
""", all_symbols)

get_unaryop = _getsymbol("""
    UAdd +   USub -   Invert ~   Not not
""", all_symbols)

get_anyop = _getsymbol(all_symbols)


class ExplicitNodeVisitor(ast.NodeVisitor):
    """This expands on the ast module's NodeVisitor class
    to remove any implicit visits.

    """

    def abort_visit(node):  # XXX: self?
        msg = 'No defined handler for node of type %s'
        raise AttributeError(msg % node.__class__.__name__)

    def visit(self, node, abort=abort_visit):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, abort)
        return visitor(node)


def parsefile(fname):
    """Parse a python file into an AST.

       This is a very thin wrapper around ast.parse

        TODO: Handle encodings other than the default (issue #26)
    """
    with open(fname, 'r') as f:
        fstr = f.read()
    fstr = fstr.replace('\r\n', '\n').replace('\r', '\n')
    if not fstr.endswith('\n'):
        fstr += '\n'
    return ast.parse(fstr, filename=fname)


def finfo(codeobj):
    """Returns the file and line number of a code object.
        If the code object has a __file__ attribute (e.g. if
        it is a module), then the returned line number will
        be 0

    """
    fname = getattr(codeobj, '__file__', None)
    linenum = 0
    if fname is None:
        func_code = codeobj.__code__
        fname = func_code.co_filename
        linenum = func_code.co_firstlineno
    fname = fname.replace('.pyc', '.py')
    return fname, linenum


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
        key = finfo(codeobj)
        result = cache.get(key)
        if result is not None:
            return result
        fname = key[0]
        cache[(fname, 0)] = mod_ast = parsefile(fname)
        for obj in mod_ast.body:
            if not isinstance(obj, ast.FunctionDef):
                continue
            cache[(fname, obj.lineno)] = obj
        return cache[key]

codetoast = CodeToAst()


class StripLineCol(ast.NodeVisitor):
    """Strip the line and column numbers from the tree

    """

    def visit(self, node):
        """Visit a node."""
        for kill in ('lineno', 'col_offset'):
            if hasattr(node, kill):
                delattr(node, kill)

striplinecol = StripLineCol().visit


def pyfiles(srctree, ignore=None):
    """Return all the python files in a source tree

       Ignores any path that contains the ignore string
    """

    for srcpath, _, fnames in os.walk(srctree):
        # Avoid infinite recursion for silly users
        if ignore is not None and ignore in srcpath:
            continue
        for fname in (x for x in fnames if x.endswith('.py')):
            yield srcpath, fname
