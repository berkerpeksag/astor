# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2012-2015 Patrick Maupin

This module provides data and functions for mapping
AST nodes to symbols and precedences.

"""

import ast

op_data = """
              Or   or            4
             And   and           6
             Not   not           8
              Eq   ==           10
              Gt   >            10
             GtE   >=           10
              In   in           10
              Is   is           10
           NotEq   !=           10
              Lt   <            10
             LtE   <=           10
           NotIn   not in       10
           IsNot   is not       10
           BitOr   |            12
          BitXor   ^            14
          BitAnd   &            16
          LShift   <<           18
          RShift   >>           18
             Add   +            20
             Sub   -            20
            Mult   *            22
             Div   /            22
             Mod   %            22
        FloorDiv   //           22
         MatMult   @            22
            UAdd   +            24
            USub   -            24
          Invert   ~            24
             Pow   **           26
"""

op_data = [x.split() for x in op_data.splitlines()]
op_data = [(x[0], ' '.join(x[1:-1]), int(x[-1])) for x in op_data if x]
precedence_data = dict((getattr(ast, x, None), z) for x, y, z in op_data)
symbol_data = dict((getattr(ast, x, None), y) for x, y, z in op_data)

def get_op_symbol(obj, fmt='%s', symbol_data=symbol_data, type=type):
    """Given an AST node object, returns a string containing the symbol.
    """
    return fmt % symbol_data[type(obj)]

def get_op_precedence(obj, precedence_data=precedence_data, type=type):
    """Given an AST node object, returns the precedence.
    """
    return precedence_data[type(obj)]
