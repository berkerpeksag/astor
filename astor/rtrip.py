#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015 Patrick Maupin

Usage:

    python -m astor.rtrip [readonly] [<source>]


This utility tests round-tripping of Python source to AST
and back to source.

    .. versionadded:: 0.6

If readonly is specified, then the source will be tested,
but no files will be written.

if the source is specified to be "stdin" (without quotes)
then any source entered at the command line will be compiled
into an AST, converted back to text, and then compiled to
an AST again, and the results will be displayed to stdout.

If neither readonly nor stdin is specified, then rtrip
will create a mirror directory named tmp_rtrip and will
recursively round-trip all the Python source from the source
into the tmp_rtrip dir, after compiling it and then reconstituting
it through code_gen.to_source.

If the source is not specified, the entire Python library will be used.

The purpose of rtrip is to place Python code into a canonical form.

This is useful both for functional testing of astor, and for
validating code edits.

For example, if you make manual edits for PEP8 compliance,
you can diff the rtrip output of the original code against
the rtrip output of the edited code, to insure that you
didn't make any functional changes.

For testing astor itself, it is useful to point to a big codebase,
e.g::

    python -m astor.rtrip

to roundtrip the standard library.

If any round-tripped files fail to be built or to match, the
tmp_rtrip directory will also contain fname.srcdmp and fname.dstdmp,
which are textual representations of the ASTs.


Note 1:
        The canonical form is only canonical for a given version of
        this module and the astor toolbox.  It is not guaranteed to
        be stable.  The only desired guarantee is that two source modules
        that parse to the same AST will be converted back into the same
        canonical form.

Note 2:
        This tool WILL TRASH the tmp_rtrip directory (unless readonly
        is specified) -- as far as it is concerned, it OWNS that directory.

Note 3: Why is it "readonly" and not "-r"?  Because python -m slurps
        all the thingies starting with the dash.
"""

import sys
import os
import ast
import shutil
import logging

from astor.code_gen import to_source
from astor.file_util import code_to_ast
from astor.node_util import (allow_ast_comparison, dump_tree,
                             strip_tree, fast_compare)


dsttree = 'tmp_rtrip'


def convert(srctree, dsttree=dsttree, readonly=False, dumpall=False,
            ignore_exceptions=False, fullcomp=False):
    """Walk the srctree, and convert/copy all python files
    into the dsttree

    """

    if fullcomp:
        allow_ast_comparison()

    parse_file = code_to_ast.parse_file
    find_py_files = code_to_ast.find_py_files
    srctree = os.path.normpath(srctree)

    if not readonly:
        dsttree = os.path.normpath(dsttree)
        logging.info('')
        logging.info('Trashing ' + dsttree)
        shutil.rmtree(dsttree, True)

    unknown_src_nodes = set()
    unknown_dst_nodes = set()
    badfiles = set()
    broken = []
    # TODO: When issue #26 resolved, remove UnicodeDecodeError
    handled_exceptions = SyntaxError, UnicodeDecodeError

    oldpath = None

    allfiles = find_py_files(srctree, None if readonly else dsttree)
    for srcpath, fname in allfiles:
        # Create destination directory
        if not readonly and srcpath != oldpath:
            oldpath = srcpath
            if srcpath >= srctree:
                dstpath = srcpath.replace(srctree, dsttree, 1)
                if not dstpath.startswith(dsttree):
                    raise ValueError("%s not a subdirectory of %s" %
                                     (dstpath, dsttree))
            else:
                assert srctree.startswith(srcpath)
                dstpath = dsttree
            os.makedirs(dstpath)

        srcfname = os.path.join(srcpath, fname)
        logging.info('Converting %s' % srcfname)
        try:
            srcast = parse_file(srcfname)
        except handled_exceptions:
            badfiles.add(srcfname)
            continue


        try:
            dsttxt = to_source(srcast)
        except:
            if not ignore_exceptions:
                raise
            dsttxt = ''

        if not readonly:
            dstfname = os.path.join(dstpath, fname)
            try:
                with open(dstfname, 'w') as f:
                    f.write(dsttxt)
            except UnicodeEncodeError:
                badfiles.add(dstfname)

        # As a sanity check, make sure that ASTs themselves
        # round-trip OK
        try:
            dstast = ast.parse(dsttxt) if readonly else parse_file(dstfname)
        except SyntaxError:
            dstast = []
        if fullcomp:
            unknown_src_nodes.update(strip_tree(srcast))
            unknown_dst_nodes.update(strip_tree(dstast))
            bad = srcast != dstast
        else:
            bad = not fast_compare(srcast, dstast)
        if dumpall or bad:
            srcdump = dump_tree(srcast)
            dstdump = dump_tree(dstast)
            logging.warning('    calculating dump -- %s' %
                            ('bad' if bad else 'OK'))
            if bad:
                broken.append(srcfname)
            if dumpall or bad:
                if not readonly:
                    try:
                        with open(dstfname[:-3] + '.srcdmp', 'w') as f:
                            f.write(srcdump)
                    except UnicodeEncodeError:
                        badfiles.add(dstfname[:-3] + '.srcdmp')
                    try:
                        with open(dstfname[:-3] + '.dstdmp', 'w') as f:
                            f.write(dstdump)
                    except UnicodeEncodeError:
                        badfiles.add(dstfname[:-3] + '.dstdmp')
                elif dumpall:
                    sys.stdout.write('\n\nAST:\n\n    ')
                    sys.stdout.write(srcdump.replace('\n', '\n    '))
                    sys.stdout.write('\n\nDecompile:\n\n    ')
                    sys.stdout.write(dsttxt.replace('\n', '\n    '))
                    sys.stdout.write('\n\nNew AST:\n\n    ')
                    sys.stdout.write('(same as old)' if dstdump == srcdump
                                     else dstdump.replace('\n', '\n    '))
                    sys.stdout.write('\n')

    if badfiles:
        logging.warning('\nFiles not processed due to syntax errors:')
        for fname in sorted(badfiles):
            logging.warning('    %s' % fname)
    if broken:
        logging.warning('\nFiles failed to round-trip to AST:')
        for srcfname in broken:
            logging.warning('    %s' % srcfname)

    ok_to_strip = 'col_offset _precedence _use_parens lineno _p_op _pp'
    ok_to_strip = set(ok_to_strip.split())
    bad_nodes = (unknown_dst_nodes | unknown_src_nodes) - ok_to_strip
    if bad_nodes:
        logging.error('\nERROR -- UNKNOWN NODES STRIPPED: %s' % bad_nodes)
    logging.info('\n')


def usage(msg):
    raise SystemExit(textwrap.dedent("""

        Error: %s

        Usage:

            python -m astor.rtrip [readonly] [<source>]


        This utility tests round-tripping of Python source to AST
        and back to source.

        If readonly is specified, then the source will be tested,
        but no files will be written.

        if the source is specified to be "stdin" (without quotes)
        then any source entered at the command line will be compiled
        into an AST, converted back to text, and then compiled to
        an AST again, and the results will be displayed to stdout.

        If neither readonly nor stdin is specified, then rtrip
        will create a mirror directory named tmp_rtrip and will
        recursively round-trip all the Python source from the source
        into the tmp_rtrip dir, after compiling it and then reconstituting
        it through code_gen.to_source.

        If the source is not specified, the entire Python library will be used.

        """) % msg)

if __name__ == '__main__':
    import textwrap

    args = sys.argv[1:]

    readonly = 'readonly' in args
    if readonly:
        args.remove('readonly')

    if not args:
        args = [os.path.dirname(textwrap.__file__)]

    if len(args) > 1:
        usage("Too many arguments")

    fname, = args
    dumpall = False
    if not os.path.exists(fname):
        dumpall = fname == 'stdin' or usage("Cannot find directory %s" % fname)

    logging.basicConfig(format='%(msg)s', level=logging.INFO)
    convert(fname, readonly=readonly or dumpall, dumpall=dumpall)
