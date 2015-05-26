# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015 Patrick Maupin

Pretty-print strings for the decompiler

We either return the repr() of the string,
or try to format it as a triple-quoted string.

This is a lot harder than you would think.

This has lots of Python 2 / Python 3 ugliness.

"""

import re
import logging

try:
    special_unicode = unicode
except NameError:
    class special_unicode(object):
        pass

try:
    basestring = basestring
except NameError:
    basestring = str


def _get_line(current_output):
    """ Back up in the output buffer to
        find the start of the current line,
        and return the entire line.
    """
    myline = []
    index = len(current_output)
    while index:
        index -= 1
        try:
            s = str(current_output[index])
        except:
            raise
        myline.append(s)
        if '\n' in s:
            break
    myline = ''.join(reversed(myline))
    return myline.rsplit('\n', 1)[-1]


def _properly_indented(s, current_line):
    line_indent = len(current_line) - len(current_line.lstrip())
    mylist = s.split('\n')[1:]
    mylist = [x.rstrip() for x in mylist]
    mylist = [x for x in mylist if x]
    if not s:
        return False
    counts = [(len(x) - len(x.lstrip())) for x in mylist]
    return counts and min(counts) >= line_indent

mysplit = re.compile(r'(\\|\"\"\"|\"$)').split
replacements = {'\\': '\\\\', '"""': '""\\"', '"': '\\"'}


def _prep_triple_quotes(s, mysplit=mysplit, replacements=replacements):
    """ Split the string up and force-feed some replacements
        to make sure it will round-trip OK
    """

    s = mysplit(s)
    s[1::2] = (replacements[x] for x in s[1::2])
    return ''.join(s)


def pretty_string(s, embedded, current_output, min_trip_str=20, max_line=100):
    """There are a lot of reasons why we might not want to or
       be able to return a triple-quoted string.  We can always
       punt back to the default normal string.
    """

    default = repr(s)

    # Punt on abnormal strings
    if (isinstance(s, special_unicode) or not isinstance(s, basestring)):
        return default

    len_s = len(default)
    current_line = _get_line(current_output)
    if current_line.strip():
        if embedded and '\n' not in s:
            return default

        if len_s < min_trip_str:
            return default

        total_len = len(current_line) + len_s
        if total_len < max_line and not _properly_indented(s, current_line):
            return default

    fancy = '"""%s"""' % _prep_triple_quotes(s)

    # Sometimes this doesn't work.  One reason is that
    # the AST has no understanding of whether \r\n was
    # entered that way in the string or was a cr/lf in the
    # file.  So we punt just so we can round-trip properly.

    try:
        if eval(fancy) == s and '\r' not in fancy:
            return fancy
    except:
        pass
    """
    logging.warning("***String conversion did not work\n")
    #print (eval(fancy), s)
    print
    print (fancy, repr(s))
    print
    """
    return default
