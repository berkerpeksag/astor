# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2012 (c) Patrick Maupin
Copyright 2013 (c) Berker Peksag

"""

from .code_gen import to_source  # NOQA
from .node_util import iter_node, strip_tree, dump_tree
from .node_util import ExplicitNodeVisitor
from .file_util import CodeToAst, code_to_ast  # NOQA
from .op_util import get_op_symbol, get_op_precedence  # NOQA
from .op_util import symbol_data
from .tree_walk import TreeWalk  # NOQA

__version__ = '0.6'


# DEPRECATED!!!

# These aliases support old programs.  Please do not use in future.

# NOTE: We should think hard about what we want to export,
#      and not just dump everything here.  Some things
#      will never be used by other packages, and other
#      things could be accessed from their submodule.

def deprecated(old_name, new_name, new_fn):
    """
    Creates a wrapped version of `new_fn` that prints a deprecation message

    * old_name : the name of the deprecated function
    * new_name : the name of the function replacing `old_name`
    * new_fn   : the `new_name` function object
    """
    def wrapped(*args, **kwargs):
        print("Warning: astor.{} is deprecated and will be removed in the 0.7 release, use astor.{} instead.".format(old_name, new_name))
        return new_fn(*args, **kwargs)
    return wrapped

deprecated_functions = [
    ("get_boolop"  , "get_op_symbol"),
    ("get_binop"   , "get_op_symbol"),
    ("get_cmpop"   , "get_op_symbol"),
    ("get_unaryop" , "get_op_symbol"),
    ("get_anyop"   , "get_op_symbol"),
    ("parsefile"   , "code_to_ast.parse_file"),
    ("codetoast"   , "code_to_ast"),
    ("dump"        , "dump_tree"),
    ("all_symbols" , "symbol_data"),
    ("treewalk"    , "tree_walk"),
    ("codegen"     , "code_gen")
]

for old_name, new_fn in deprecated_functions:
    exec("{old_name} = deprecated(\"{old_name}\", \"{new_fn}\", {new_fn})".format(old_name=old_name, new_fn=new_fn))
