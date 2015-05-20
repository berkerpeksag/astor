#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright 2015 (c) Patrick Maupin

Usage:

    python -m astor.anti8 [readonly] <srcdir>

This will create a mirror directory named tmp_anti8 and will
recursively round-trip all the Python source from the srcdir
into the tmp_anti8 dir, after compiling it and then reconstituting
it through codegen.

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

Note 4: I lied a little bit in notes 2 and 3.  You can also pass "readonly" as
        a command line option for readonly (non-destructive mode).
        This is primarily useful for testing astor itself.

Note 5: Why is it "readonly" and not "-r"?  Because python -m slurps
        all the thingies starting with the dash.
"""

import sys
import os
import ast
import shutil
import logging

#Avoid import loops
from .misc import parsefile, striplinecol,  pyfiles
from .codegen import to_source

def dump(top, dict=dict, list=list, type=type, isinstance=isinstance, len=len):

    def dump(node, indent):
        if isinstance(node, dict):
            for key, value in sorted(node.items()):
                result.append('%s%s' % (indent, key))
                dump(value, indent+'    ')
        elif isinstance(node, list):
            for i, value in enumerate(node):
                result.append('%s[%s]' % (indent, i))
                dump(value, indent+'    ')
        else:
            result.append('%s%s' % (indent, repr(node)))

    result = []
    dump(top, '')
    return '\n'.join(result)

def convert(srctree, dsttree='tmp_anti8', readonly=False):
    """Walk the srctree, and convert/copy all python files
    into the dsttree

    """

    srctree = os.path.normpath(srctree)

    if not readonly:
        dsttree = os.path.normpath(dsttree)
        logging.info('')
        logging.info('Trashing ' + dsttree)
        shutil.rmtree(dsttree, True)

    badfiles = set()
    broken = []
    #TODO: When issue #26 resolved, remove UnicodeDecodeError
    handled_exceptions = SyntaxError, UnicodeDecodeError

    oldpath = ''
    for srcpath, fname in pyfiles(srctree, None if readonly else dsttree):
        # Create destination directory
        if not readonly and srcpath != oldpath:
            oldpath = srcpath
            dstpath = srcpath.replace(srctree, dsttree, 1)
            if not dstpath.startswith(dsttree):
                raise ValueError("%s not a subdirectory of %s" %
                                                (dstpath, dsttree))
            os.makedirs(dstpath)

        srcfname = os.path.join(srcpath, fname)
        logging.info('Converting ' + srcfname)
        try:
            srcast = parsefile(srcfname)
        except handled_exceptions:
            badfiles.add(srcfname)
            continue

        dsttxt = to_source(srcast)

        if not readonly:
            dstfname = os.path.join(dstpath, fname)
            with open(dstfname, 'w') as f:
                f.write(dsttxt)

        # As a sanity check, make sure that ASTs themselves
        # round-trip OK
        dstast = ast.parse(dsttxt) if readonly else parsefile(dstfname)
        srcast = striplinecol(srcast)
        dstast = striplinecol(dstast)
        if srcast != dstast:
            broken.append((srcfname, srcast, dstast))

    if badfiles:
        logging.warning('')
        logging.warning('Files not processed due to syntax errors:')
        for fname in sorted(badfiles):
            logging.warning('    ' + fname)
    if broken:
        logging.warning('')
        logging.warning('Files failed to round-trip to AST:')
        for i, (fname, srcast, dstast) in enumerate(sorted(broken)):
            logging.warning('    ' + fname)
            with open('1_bad_anti8_%d.txt' % i, 'w') as f:
                f.write(dump(srcast))
            with open('2_bad_anti8_%d.txt' % i, 'w') as f:
                f.write(dump(dstast))

if __name__ == '__main__':
    readonly = 'readonly' in sys.argv
    if readonly:
        sys.argv.remove('readonly')

    srctree, = sys.argv[1:]
    logging.basicConfig(format='%(msg)s', level=logging.INFO)
    if convert(srctree, readonly=readonly):
        raise SystemExit('\nWARNING: Not all files converted\n')
