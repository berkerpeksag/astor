#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015 Patrick Maupin

Usage:

    python -m astor.rtrip [readonly] [<srcdir>]


If readonly is specified, then the source will be tested,
but no files will be written.

If srcdir is not specified, the standard library will be used.

This will create a mirror directory named tmp_rtrip and will
recursively round-trip all the Python source from the srcdir
into the tmp_rtrip dir, after compiling it and then reconstituting
it through code_gen.to_source.

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

#Avoid import loops
from .code_gen import to_source
from .file_util import code_to_ast
from .node_util import allow_ast_comparison, dump_tree, strip_tree


def convert(srctree, dsttree='tmp_rtrip', readonly=False):
    """Walk the srctree, and convert/copy all python files
    into the dsttree

    """

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
    #TODO: When issue #26 resolved, remove UnicodeDecodeError
    handled_exceptions = SyntaxError, UnicodeDecodeError

    oldpath = ''

    allfiles = find_py_files(srctree, None if readonly else dsttree)
    for srcpath, fname in allfiles:
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
            srcast = parse_file(srcfname)
        except handled_exceptions:
            badfiles.add(srcfname)
            continue

        dsttxt = to_source(srcast)

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
        unknown_src_nodes.update(strip_tree(srcast))
        unknown_dst_nodes.update(strip_tree(dstast))
        if srcast != dstast:
            srcdump = dump_tree(srcast)
            dstdump = dump_tree(dstast)
            bad = srcdump != dstdump
            logging.warning('    calculating dump -- %s' % ('bad' if bad else 'OK'))
            if bad:
                broken.append(srcfname)
                if not readonly:
                    try:
                        with open(dstfname[:-3] +'.srcdmp', 'w') as f:
                            f.write(srcdump)
                    except UnicodeEncodeError:
                        badfiles.add(dstfname[:-3] +'.srcdmp')
                    try:
                        with open(dstfname[:-3] +'.dstdmp', 'w') as f:
                            f.write(dstdump)
                    except UnicodeEncodeError:
                        badfiles.add(dstfname[:-3] +'.dstdmp')

    if badfiles:
        logging.warning('\nFiles not processed due to syntax errors:')
        for fname in sorted(badfiles):
            logging.warning('    %s' % fname)
    if broken:
        logging.warning('\nFiles failed to round-trip to AST:')
        for srcfname in broken:
            logging.warning('    %s' % srcfname)

    ok_to_strip = set(['col_offset', '_precedence', '_use_parens', 'lineno'])
    bad_nodes = (unknown_dst_nodes | unknown_src_nodes) - ok_to_strip
    if bad_nodes:
        logging.error('\nERROR -- UNKNOWN NODES STRIPPED: %s' % bad_nodes)
    logging.info('\n')

if __name__ == '__main__':
    import textwrap

    args = sys.argv[1:]

    readonly = 'readonly' in args
    if readonly:
        args.remove('readonly')

    if not args:
        args = [os.path.dirname(textwrap.__file__)]
    msg = "Too many arguments" if len(args) != 1 else (
          "%s is not a directory" % args[0] if not os.path.isdir(args[0])
          else "")

    if msg:
        raise SystemExit(textwrap.dedent("""

            Error: %s

            Usage:

                python -m astor.rtrip [readonly] [<srcdir>]


            If readonly is specified, then the source will be tested,
            but no files will be written.

            If srcdir is not specified, the standard library will be used.

            This will create a mirror directory named tmp_rtrip and will
            recursively round-trip all the Python source from the srcdir
            into the tmp_rtrip dir, after compiling it and then reconstituting
            it through code_gen.to_source.

            """) % msg)

    logging.basicConfig(format='%(msg)s', level=logging.INFO)
    if convert(args[0], readonly=readonly):
        raise SystemExit('\nWARNING: Not all files converted\n')
