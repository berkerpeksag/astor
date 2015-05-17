#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2015 (c) Patrick Maupin

The purpose of anti8 is to place Python code into a canonical form --
     that just happens to be about as far away from PEP 8 as you can get.

How is this possibly useful?

Well, for a start, since it is a canonical form, you can compare the anti8
representation of a source tree against the anti8 representation of the
same tree after a PEP8 tool was run on it.

Or, maybe more importantly, after manual edits were made in the name
of PEP8.  Trust, but verify.

Note 1: The canonical form is only canonical for a given version of
        this module and the astor toolbox.  It is not guaranteed to
        be stable.  The only desired guarantee is that two source modules
        that parse to the same AST will be converted back into the same
        canonical form.

Note 2: This tool WILL TRASH the tmp_anti8 directory -- as far as it is
        concerned, it OWNS that directory.

Note 3: This tools WILL CRASH if you don't give it exactly one parameter
        on the command line -- the top of the tree you want to apply
        anti8 to.  You can read the traceback and figure this out, right?
"""

import sys
import os
import ast
import shutil
import logging

try:
    import astor
except ImportError:
    exampledir = os.path.dirname(os.path.abspath(sys.argv[0]))
    rootdir = os.path.dirname(exampledir)
    sys.path.insert(0, rootdir)
    import astor


class StripLineCol(ast.NodeVisitor):
    """Strip the line and column numbers from the tree

    """

    def visit(self, node):
        """Visit a node."""
        for kill in ('lineno', 'col_offset'):
            if hasattr(node, kill):
                delattr(node, kill)

striplinecol = StripLineCol().visit


def convert(srctree, dsttree='tmp_anti8'):
    """Walk the srctree, and convert/copy all python files
    into the dsttree

    """

    srctree = os.path.normpath(srctree)
    dsttree = os.path.normpath(dsttree)

    logging.info('')
    logging.info('Trashing ' + dsttree)
    shutil.rmtree(dsttree, True)

    for srcpath, _, fnames in os.walk(srctree):
        # Avoid infinite recursion for silly users
        if dsttree in srcpath:
            continue
        dstpath = srcpath.replace(srctree, dsttree, 1)
        logging.info('')
        logging.info('Creating ' + dstpath)
        os.mkdir(dstpath)
        for fname in (x for x in fnames if x.endswith('.py')):
            logging.info('    Converting ' + fname)
            srcfname = os.path.join(srcpath, fname)
            dstfname = os.path.join(dstpath, fname)
            srcast = astor.parsefile(srcfname)
            with open(dstfname, 'w') as f:
                f.write(astor.to_source(srcast))

            # As a sanity check, make sure that ASTs themselves
            # round-trip OK
            dstast = astor.parsefile(dstfname)
            if striplinecol(srcast) != striplinecol(dstast):
                raise ValueError('Round trip of %s failed' % srcfname)


if __name__ == '__main__':
    srctree, = sys.argv[1:]
    logging.basicConfig(format='%(msg)s', level=logging.INFO)
    convert(srctree)
