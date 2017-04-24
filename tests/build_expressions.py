#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015 Patrick Maupin

This module generates a lot of permutations of Python
expressions, and dumps them into a python module
all_expr_x_y.py (where x and y are the python version tuple)
as a string.

This string is later used by check_expressions.

This module takes a loooooooooong time to execute.

"""

import sys
import collections
import itertools
import textwrap
import ast
import astor

all_operators = (
            # Selected special operands
            '3 -3 () yield',
            # operators with one parameter
            'yield lambda_: not + - ~ $, yield_from',
            # operators with two parameters
            'or and == != > >= < <= in not_in is is_not '
            '| ^ & << >> + - * / % // @ ** for$in$ $($) $[$] . '
            '$,$ ',
            # operators with 3 parameters
            '$if$else$ $for$in$'
        )


select_operators = (
            # Selected special operands -- remove
            # some at redundant precedence levels
            '-3',
            # operators with one parameter
            'yield lambda_: not - ~ $,',
            # operators with two parameters
            'or and == in is '
            '| ^ & >> - % ** for$in$ $($) . ',
            # operators with 3 parameters
            '$if$else$  $for$in$'
        )


def get_primitives(base):
    """Attempt to return formatting strings for all operators,
       and selected operands.
       Here, I use the term operator loosely to describe anything
       that accepts an expression and can be used in an additional
       expression.
    """

    operands = []
    operators = []
    for nparams, s in enumerate(base):
        s = s.replace('%', '%%').split()
        for s in (x.replace('_', ' ') for x in s):
            if nparams and '$' not in s:
                assert nparams in (1, 2)
                s = '%s%s$' % ('$' if nparams == 2 else '', s)
            assert nparams == s.count('$'), (nparams, s)
            s = s.replace('$', ' %s ').strip()

            # Normalize the spacing
            s = s.replace(' ,', ',')
            s = s.replace(' . ', '.')
            s = s.replace(' [ ', '[').replace(' ]', ']')
            s = s.replace(' ( ', '(').replace(' )', ')')
            if nparams == 1:
                s = s.replace('+ ', '+')
                s = s.replace('- ', '-')
                s = s.replace('~ ', '~')

            if nparams:
                operators.append((s, nparams))
            else:
                operands.append(s)
    return operators, operands


def get_sub_combinations(maxop):
    """Return a dictionary of lists of combinations suitable
       for recursively building expressions.

       Each dictionary key is a tuple of (numops, numoperands),
       where:

            numops is the number of operators we
            should build an expression for

            numterms is the number of operands required
            by the current operator.

        Each list contains all permutations of the number
        of operators that the recursively called function
        should use for each operand.
    """
    combo = collections.defaultdict(list)
    for numops in range(maxop+1):
        if numops:
            combo[numops, 1].append((numops-1,))
        for op1 in range(numops):
            combo[numops, 2].append((op1, numops - op1 - 1))
            for op2 in range(numops - op1):
                combo[numops, 3].append((op1, op2, numops - op1 - op2 - 1))
    return combo


def get_paren_combos():
    """This function returns a list of lists.
       The first list is indexed by the number of operands
       the current operator has.

       Each sublist contains all permutations of wrapping
       the operands in parentheses or not.
    """
    results = [None] * 4
    options = [('%s', '(%s)')]
    for i in range(1, 4):
        results[i] = list(itertools.product(*(i * options)))
    return results


def operand_combo(expressions, operands, max_operand=13):
    op_combos = []
    operands = list(operands)
    operands.append('%s')
    for n in range(max_operand):
        this_combo = []
        op_combos.append(this_combo)
        for i in range(n):
            for op in operands:
                mylist = ['%s'] * n
                mylist[i] = op
                this_combo.append(tuple(mylist))
    for expr in expressions:
        expr = expr.replace('%%', '%%%%')
        for op in op_combos[expr.count('%s')]:
            yield expr % op


def build(numops=2, all_operators=all_operators, use_operands=False,
          # Runtime optimization
          tuple=tuple):
    operators, operands = get_primitives(all_operators)
    combo = get_sub_combinations(numops)
    paren_combos = get_paren_combos()
    product = itertools.product
    try:
        izip = itertools.izip
    except AttributeError:
        izip = zip

    def recurse_build(numops):
        if not numops:
            yield '%s'
        for myop, nparams in operators:
            myop = myop.replace('%%', '%%%%')
            myparens = paren_combos[nparams]
            # print combo[numops, nparams]
            for mycombo in combo[numops, nparams]:
                # print mycombo
                call_again = (recurse_build(x) for x in mycombo)
                for subexpr in product(*call_again):
                    for parens in myparens:
                        wrapped = tuple(x % y for (x, y)
                                        in izip(parens, subexpr))
                        yield myop % wrapped
    result = recurse_build(numops)
    return operand_combo(result, operands) if use_operands else result


def makelib():
    parse = ast.parse
    dump_tree = astor.dump_tree

    def default_value(): return 1000000, ''
    mydict = collections.defaultdict(default_value)

    allparams = [tuple('abcdefghijklmnop'[:x]) for x in range(13)]
    alltxt = itertools.chain(build(1, use_operands=True),
                             build(2, use_operands=True),
                             build(3, select_operators))

    yieldrepl = list(('yield %s %s' % (operator, operand),
                      'yield %s%s' % (operator, operand))
                     for operator in '+-' for operand in '(ab')
    yieldrepl.append(('yield[', 'yield ['))
    # alltxt = itertools.chain(build(1), build(2))
    badexpr = 0
    goodexpr = 0
    silly = '3( 3.( 3[ 3.['.split()
    for expr in alltxt:
        params = allparams[expr.count('%s')]
        expr %= params
        try:
            myast = parse(expr)
        except:
            badexpr += 1
            continue
        goodexpr += 1
        key = dump_tree(myast)
        expr = expr.replace(', - ', ', -')
        ignore = [x for x in silly if x in expr]
        if ignore:
            continue
        if 'yield' in expr:
            for x in yieldrepl:
                expr = expr.replace(*x)
        mydict[key] = min(mydict[key], (len(expr), expr))
    print(badexpr, goodexpr)

    stuff = [x[1] for x in mydict.values()]
    stuff.sort()

    lineend = '\n'.encode('utf-8')
    with open('all_expr_%s_%s.py' % sys.version_info[:2], 'wb') as f:
        f.write(textwrap.dedent('''
            # AUTOMAGICALLY GENERATED!!!  DO NOT MODIFY!!
            #
            all_expr = """
            ''').encode('utf-8'))
        for item in stuff:
            f.write(item.encode('utf-8'))
            f.write(lineend)
        f.write('"""\n'.encode('utf-8'))


if __name__ == '__main__':
    makelib()
