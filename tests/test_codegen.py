#!/usr/bin/env python
"""
Part of the astor library for Python AST manipulation

License: BSD

Copyright 2012 (c) Patrick Maupin
"""


import fnmatch
import os
import sys
import ast

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import astor


def findpy(root):
    if isinstance(root, str):
        if os.path.isfile(root):
            if root.endswith('.py'):
                yield root
            return
        for fname in os.listdir(root):
            fname = os.path.join(root, fname)
            if os.path.isdir(fname):
                for fname in findpy(fname):
                    yield fname
            elif fnmatch.fnmatch(fname, '*.py'):
                yield fname
    else:
        for dirname in root:
            for fname in findpy(dirname):
                yield fname

def testone(fname, f1=None, f2=None):
    try:
        ast1 = astor.parsefile(fname)
    except (SyntaxError, UnicodeDecodeError):
        print("IGNORED %s" % fname)
        return
    dump1 = astor.dump(ast1)
    reconstitute = '# -*- coding: utf-8 -*-\n' + astor.to_source(ast1)
    ast2 = ast.parse(reconstitute, fname)
    dump2 = astor.dump(ast2)
    ok = dump1 == dump2
    print('%-8s%s' % ('OK' if dump1 == dump2 else 'FAIL', fname))
    if not ok and f1 is not None and f2 is not None:
        f1.write('\n\n***************************************\n%s\n***************************************\n\n\n' % fname)
        f2.write('\n\n***************************************\n%s\n***************************************\n\n\n' % fname)
        f1.write(dump1)
        f2.write(dump2)
        f = open('bad.txt', 'w')
        f.write(reconstitute)
        f.close()
    return ok


def go(root, stoponfail=True, f1=None, f2=None):
    for fname in findpy(root or os.path.dirname(fnmatch.__file__)):
        if not testone(fname, f1, f2) and stoponfail:
            break


if __name__ == '__main__':
    f1 = open('test_codegen_dump_1.txt', 'w')
    f2 = open('test_codegen_dump_2.txt', 'w')
    go(sys.argv[1:], False, f1, f2)
