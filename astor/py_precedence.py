# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015 Patrick Maupin

This module contains a class that can annotate an
AST with Python precedence information for
prettier decompilation (allows removal of parentheses
when it is safe).

"""

import ast
import sys

from .tree_walk import TreeWalk
from .op_util import get_op_precedence

class SetPrecedence(TreeWalk):
    """This class is used to decorate the ast.  Currently it adds
       two different members to some nodes:  _precedence is the
       parse precedence, which is used to compute _use_parens,
       which defines whether parentheses are required.

        This class is based off the TreeWalk class.  It uses
        two features of that class:

            - parent nodes are available for inspection
            - Subnodes can be explicitly walked.  A node handler
              should return True to indicate it has done this.

        Precedences are defined as even numbers.  Bumping
        to an odd number allows definition of an intermediate
        precedence that is still lower than the next precedence,
        yet higher than another operator of the same precedence,
        to force parentheses in a few edge cases.
    """

    def pre_Subscript(self):
        """Set a really high precedence to require parentheses
           if we are subscripting an expression.
        """
        node = self.cur_node
        node._precedence = get_op_precedence(node)
        self.walk(node.value)
        del node._precedence
        self.walk(node.slice)
        return True

    def set_precedence(self, node, op, subnodes=(), bump0=0, bump1=0):
        """Generic precedence setter -- handles incrementing
           precedence before processing subnodes.
        """
        precedence = get_op_precedence(op) if not isinstance(op, int) else op
        parent_precedence = getattr(self.parent, '_precedence', -1)
        node._use_parens = precedence < parent_precedence
        if subnodes:
            node._precedence = precedence + bump0
            self.walk(subnodes[0])
            node._precedence = precedence + bump1
            for node in subnodes[1:]:
                self.walk(node)
        # If we did the subnodes, do not recurse any further
        return subnodes

    def pre_BinOp(self, powop=ast.Pow):
        """Handle binary operations.  Always bump this node's
           precedence when walking the rh node (think proper
           processing of a / (b / c), and also bump this
           node's precedence when processing the lh node
           of an exponentiation operator.
        """
        node = self.cur_node
        op = node.op
        ispow = isinstance(op, powop)
        subnodes = node.left, node.right
        return self.set_precedence(node, op, subnodes, ispow, 1)

    def pre_BoolOp(self):
        """ To faithfully reproduce the AST in code, we bump the
            precedence on the lh side as well as the right.
        """
        node = self.cur_node
        return self.set_precedence(node, node.op, node.values, 1, 1)

    def pre_Compare(self):
        """ Comparison ops _should_ all have the same precedence.
            We bump the precedence to handle stuff like
            (a < b) != (c < d)
        """
        node = self.cur_node
        # These should all be the same...
        precedence, = set(get_op_precedence(x) for x in node.ops)
        subnodes = [node.left] + node.comparators
        return self.set_precedence(node, precedence, subnodes, 1, 1)

    def pre_UnaryOp(self):
        node = self.cur_node
        return self.set_precedence(node, node.op, [node.operand])

    def pre_Lambda(self):
        """ Set a low, yet higher than no, precedence for our
            subnodes to see, and force parentheses on this node
            if it is inside any sort of expression.

            We could probably optimize a few more cases where
            we don't need parenthese, but lambdas and IfExprs
            are rare enough, it's probably good to have them
            for clarity anyway.
        """
        node = self.cur_node
        node._precedence = get_op_precedence(node)
        node._use_parens = getattr(self.parent, '_precedence', -1) > -1
    pre_IfExp = pre_Lambda

    def pre_Yield(self):
        """We follow the same strategy for yield as we did
           for lambda and if expressions, except that we
           need to use parentheses if they are inside
           a list (so the next list item is not assumed
           to be part of the lambda).
        """
        if not isinstance(self.parent, list):
            self.pre_Lambda()
        # Else let the default True work

    def pre_Attribute(self):
        """Set attribute to a really high precedence so
           that we force parentheses around any lhs
           expression.  Same thing for comprehensions
           and calls.
        """
        node = self.cur_node
        node._precedence = get_op_precedence(node)
    pre_comprehension = pre_Attribute
    pre_Call = pre_Attribute
    pre_Return = pre_Attribute

    def pre_Num(self):
        """There are two reasons we might need to place
           parentheses around a number:

              -- Exponentiation binds more tightly than a unary '-',
                 so if a literal number looks like it has a unary '-',
                 we should use parentheses.
              -- If we are accessing an attribute of a literal number,
                 the '.' could be confused for the definition of
                 a literal float.

        """
        parent_precedence = getattr(self.parent, '_precedence', -1)
        node = self.cur_node
        precedence = get_op_precedence(node)
        node._use_parens = precedence < parent_precedence
