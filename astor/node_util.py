# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2012 (c) Patrick Maupin
Copyright 2013 (c) Berker Peksag

"""

import ast
import sys


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


