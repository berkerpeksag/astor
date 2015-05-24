# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2012-2015 (c) Patrick Maupin
Copyright 2013-2015 (c) Berker Peksag

Utilities for node (and, by extension, tree) manipulation.
For a whole-tree approach, see the treewalk submodule.

"""

import ast


class NonExistent(object):
    """This is not the class you are looking for.
    """
    pass


def iter_node(node, name='', unknown=None,
              # Runtime optimization
              list=list, getattr=getattr, isinstance=isinstance,
              enumerate=enumerate, missing=NonExistent):
    """Iterates over an object:

       - If the object has a _fields attribute,
         it gets attributes in the order of this
         and returns name, value pairs.

       - Otherwise, if the object is a list instance,
         it returns name, value pairs for each item
         in the list, where the name is passed into
         this function (defaults to blank).

       - Can update an unknown set with information about
         attributes that do not exist in fields.
    """
    fields = getattr(node, '_fields', None)
    if fields is not None:
        for name in fields:
            value = getattr(node, name, missing)
            if value is not missing:
                yield value, name
        if unknown is not None:
            unknown.update(set(vars(node)) - set(fields))
    elif isinstance(node, list):
        for value in node:
            yield value, name


def dump_tree(node, name=None, initial_indent='', indentation='    ',
              maxline=120, maxmerged=80,
              # Runtime optimization
              iter_node=iter_node, special=ast.AST,
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


def strip_tree(node,
               # Runtime optimization
               iter_node=iter_node, special=ast.AST,
               list=list, isinstance=isinstance, type=type, len=len):
    """Strips an AST by removing all attributes not in _fields.

    Returns a set of the names of all attributes stripped.

    This canonicalizes two trees for comparison purposes.
    """
    stripped = set()

    def strip(node, indent):
        unknown = set()
        leaf = True
        for subnode, _ in iter_node(node, unknown=unknown):
            leaf = False
            strip(subnode, indent + '    ')
        if leaf:
            if isinstance(node, special):
                unknown = set(vars(node))
        stripped.update(unknown)
        for name in unknown:
            delattr(node, name)
        if hasattr(node, 'ctx'):
            delattr(node, 'ctx')
            if 'ctx' in node._fields:
                mylist = list(node._fields)
                mylist.remove('ctx')
                node._fields = mylist
    strip(node, '')
    return stripped


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


def allow_ast_comparison():
    """This ugly little monkey-patcher adds in a helper class
    to all the AST node types.  This helper class allows
    eq/ne comparisons to work, so that entire trees can
    be easily compared by Python's comparison machinery.
    Used by the anti8 functions to compare old and new ASTs.
    Could also be used by the test library.


    """

    class CompareHelper(object):
        def __eq__(self, other):
            return type(self) == type(other) and vars(self) == vars(other)

        def __ne__(self, other):
            return type(self) != type(other) or vars(self) != vars(other)

    for item in vars(ast).values():
        if type(item) != type:
            continue
        if issubclass(item, ast.AST):
            try:
                item.__bases__ = tuple(list(item.__bases__) + [CompareHelper])
            except TypeError:
                pass
