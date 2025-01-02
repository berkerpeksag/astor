# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2012 (c) Patrick Maupin
Copyright 2013 (c) Berker Peksag

"""

import warnings

from .code_gen import SourceGenerator, to_source  # NOQA
from .node_util import iter_node, strip_tree, dump_tree  # NOQA
from .node_util import ExplicitNodeVisitor  # NOQA
from .file_util import CodeToAst, code_to_ast  # NOQA
from .op_util import get_op_symbol, get_op_precedence  # NOQA
from .op_util import symbol_data  # NOQA
from .tree_walk import TreeWalk  # NOQA

__version__ = '0.8.1'

parse_file = code_to_ast.parse_file
