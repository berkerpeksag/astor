# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015 Patrick Maupin

Pretty-print strings for the decompiler

"""

def _get_line(current_output):
    myline = []
    index = len(current_output)
    while index:
        index -= 1
        s = str(current_output[index])
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

# Our attempt at rationalizing differences between Python 2 and Python 3.

try:
    basestring
except NameError:
    basestring = str
    class unicode: pass

def _prep_triple_quotes(s):
    """ You'd think there would be a utility for this somewhere,
        but I didn't find it.
    """
    for line in s.split('\n'):
        if not line:
            yield line
            continue
        line = repr(line)
        line = line[line[0].isalpha()+1:-1].split('\\\\')
        if line[0].startswith('"'):
            line[0] = '\\' + line[0]
        if line[-1].endswith('"'):
            line[-1] = line[-1][:-1] + '\\"'
        line = '\\\\'.join(line).split('"""')
        yield r'""\"'.join(line)

def pretty_string(s, current_output, min_trip_str=20, max_line=100):

    default = repr(s)
    len_s = len(default)
    if len_s < min_trip_str:
        return default

    current_line = _get_line(current_output)
    total_len = len(current_line) + len_s
    if total_len < max_line and not _properly_indented(s, current_line):
        return default

    # Use "regular" strings, whatever that means for the given Python
    fmt = '"""%s"""'
    if isinstance(s, unicode):
        #s = s.encode('utf-8', 'replace')
        fmt = 'u"""%s"""'
    elif not isinstance(s, basestring):
        #s = s.decode('utf-8', 'replace')
        pass

    fancy = fmt % '\n'.join(_prep_triple_quotes(s))

    # I don't know why this doesn't always work, and don't have
    # time to debug it right now:
    #return fancy
    return fancy if eval(fancy) == s else default
