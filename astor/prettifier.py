# -*- coding: utf-8 -*-
"""
Part of the astor library for Python AST manipulation.

License: 3-clause BSD

Copyright (c) 2015-2017 Patrick Maupin

Pretty-print source -- post-process for the decompiler

The goals of the initial cut of this engine are:

1) Do a passable, if not PEP8, job of line-wrapping.

2) Serve as an example of an interface to the decompiler
   for anybody who wants to do a better job. :)
"""

import re


class StringLiteral(str):
    """ This class is used by the source generator to create
        representations of literal strings.
    """

    is_tripled = False

    _trip_info = None
    trip_split = re.compile(r'(\\|\"\"\"|\r\n|\r|\"$)').split
    trip_sub = {'\\': '\\\\', '"""': '""\\"', '"': '\\"',
                '\r\n': '\\r\\n', '\r': '\\r'}

    def __new__(cls, s, prefix, srcinfo,
                # Constants
                s_new=str.__new__, repr=repr):
        """
        This creates a literal string for the source generator.
        The created object itself is a subclass of `str`, in a
        `repr`-style format (if evaluated, should result in a
        copy of the original string).

        All methods of this class are designed to support the
        pretty printer in this file, by determining if the
        string is better represented triple-quoted, or sliced
        up into multiple concatenated strings, or in the original
        representation.

        Parameters:

            s -- original string
            prefix -- 'f' or 'b' or 'u' or ''
            srcinfo -- Any additional info that would be useful
                       in formatting the string.

        The current SourceGenerator calls this function for `Byte`,
        `Str`, and `JoinedStr` AST nodes.  For the first two, `srcinfo`
        is None; for the latter, it is a list of all the individual
        pieces that were concatenated to make the string.  The current
        pretty printer does nothing with this information.
        """

        r = repr(s)
        if prefix:
            rp = r[:1]
            if rp.isalpha():
                assert rp == prefix, (prefix, s)
            else:
                r = prefix + r
        self = s_new(cls, r)
        self.src = s
        self.prefix = prefix
        self.srcinfo = srcinfo
        return self

    @staticmethod
    def bytes_ok(what):
        """ Figure out if we can easily represent triple-quoted bytes.

            It's an issue with Python 3 because of the non-transmutability
            of bytes and strings.
        """
        b_repr = repr(what)
        if not b_repr.startswith('b'):
            return what
        b_repr = b_repr[1:]
        u_string = what.decode('latin-1')
        u_repr = repr(u_string)
        u_repr = u_repr[1:] if u_repr.startswith('u') else u_repr
        return b_repr == u_repr and u_string

    def triple_width(self, start_pos, trip_split=trip_split,
                     trip_sub=trip_sub):
        """ Determine if we can represent the string as a triple-quoted
            string, and save off information that will let us figure
            out if it is worthwhile to do so.

            This function sets up _trip_info and returns the maximum
            width of the string.
        """
        trip_info = self._trip_info
        if trip_info is not None:
            try:
                result, indention, maxlen, lengths = trip_info
            except TypeError:
                return trip_info
            return max(start_pos + lengths[0], maxlen)

        src = self.src
        prefix = self.prefix
        if self.prefix == 'b':
            src = self.bytes_ok(src)
            if not src:
                self._trip_info = 10000000
                return 10000000
        src = trip_split(src)
        src[1::2] = [trip_sub[x] for x in src[1::2]]
        src = ''.join(src)

        result = '%s"""%s"""' % (prefix, src)
        test = result[1:] if prefix == 'f' else result
        try:
            broken = eval(test) != self.src
        except (ValueError, TypeError, SyntaxError):
            broken = True
        if broken:
            self._trip_info = 10000000
            return 10000000

        lines = result.split('\n')
        indention = [x.rstrip() for x in lines[1:]]
        indention = [x for x in indention if x]
        if not indention:
            indention = 1000000  # Stupidly big number
        else:
            counts = [(len(x) - len(x.lstrip())) for x in indention]
            indention = min(counts)
        lengths = [len(x) for x in lines]
        maxlen = max(lengths[1:]) if len(lengths) > 1 else 0
        trip_info = result, indention, maxlen, lengths
        self._trip_info = trip_info
        return max(start_pos + lengths[0], maxlen)

    @property
    def triple_quoted(self):
        """ Assumes client code has done due diligence and this is possible"""
        result = str.__new__(type(self), self._trip_info[0])
        result.prefix = self.prefix
        result.src = self.src
        result._trip_info = self._trip_info
        result.is_tripled = True
        return result

    @property
    def trip_indent(self):
        """ Assumes client code has done due diligence and this is possible"""
        return self._trip_info[1]

    @property
    def trip_lines(self):
        """ Assumes client code has done due diligence and this is possible"""
        return len(self._trip_info[-1])

    def reformat(self, start, nested, need_parens, maxlen, indentation):
        """ Reformat a string to fit better.

            Parameters:
                start -- current position on line
                nested -- true if inside parentheses
                maxlen -- maximum desired line length
                indentation -- string of spaces
        """
        width = self.triple_width(start)
        if width < len(self) + start:
            if not nested or width < maxlen + maxlen // 2:
                return self.triple_quoted, self._trip_info[-1][-1]

        indent = len(indentation)
        width = max(20, maxlen - indent - 4)
        if not nested or len(self) <= width+4 or self.prefix == 'f':
            return self, start + len(self)

        cls = type(self)
        prefix = self.prefix
        result = [cls(self.src[i:i + width], prefix, None)
                  for i in range(0, len(self.src), width)]
        result = ('\n' + indentation).join(result)
        if need_parens:
            result = '(%s)' % result
        return result, len(result[-1]) + indent + 1


class Formatter(object):
    """ This class is used by code_gen.SourceGenerator to
        help make the generated source code more readable.

        SourceGenerator uses two attributes from this class:

          - It calls `s_lit` to instantiate each literal string
            while it is traversing the tree.

          - It calls `out_format` after it has finished tree
            traversal.  `out_format` is passed a list of lists of
            strings, with each inner list representing a single source
            statement.  `out_format` should try to wrap statements
            that are too long.
    """

    maxlen = 79
    debug_long_statements = 0  # Size of max statement to output, e.g. 3000

    s_lit = StringLiteral  # NOQA -- required by code generator

    begin_delim = set('([{')
    end_delim = set(')]}')
    end_delim.add('):')
    begin_end_delim = begin_delim | end_delim

    all_statements = set(('# |@|assert |async for |async def |async with |'
                          'break|continue|class |del |except|exec |'
                          'elif |else:|for |def |global |if |import |'
                          'from |nonlocal |pass|print |raise|return|'
                          'try:|finally:|while |with |yield ').split('|'))

    wrappable_statements = set('return|yield |if |while '.split('|'))
    # Assignment operators
    assign_ops = list('|^&+-*/%@~') + '<< >> // **'.split() + ['']
    assign_ops = set(' %s= ' % x for x in assign_ops)
    first_assign_ops = assign_ops | set([': '])  # Don't forget annotations

    def out_format(self, source):
        """ out_format is passed a list of lists of strings.
            The lists alternate between linefeeds and lines.
            The lists with the line info are the interesting ones.

            The goal is to get them close to PEP 8.  This doesn't do
            it yet, but shows how to interface this class.
        """
        maxlen = self.maxlen
        for index, line in enumerate(source):
            size = self.count(line)
            too_big = size > maxlen
            last = line[-1]
            ends_lit = isinstance(last, StringLiteral)

            # Handle doc strings
            if ends_lit and len(line) == 2:
                width = last.triple_width(len(line[0]))
                if width < maxlen + maxlen // 2:
                    # Hey, they tried to indent it...
                    if width <= maxlen or too_big:
                        line[-1] = last.triple_quoted
                        continue
            if not too_big:
                continue

            # OK, line's too long and it wasn't a well-formatted docstring

            indentation = len(line[0])

            # Handle simple assignments of triple-quoted strings
            if ends_lit and size - len(last) < maxlen - 4:
                width = last.triple_width(size - len(last))
                if width < min(size, maxlen + maxlen // 2):
                    if (last.trip_indent >= indentation or
                            last.trip_lines >= 10 and len(last) >= maxlen*3):
                        line[-1] = last.triple_quoted
                        continue

            # Try to wrap it
            old_line = list(line)
            source[index] = new_line = []
            self.wrap_line(line, new_line)

            if self.debug_long_statements:
                text = ''.join(new_line)
                if (max(len(x) for x in text.split('\n')) >
                        self.debug_long_statements):
                    continue

                indent, keyword = old_line[:2]
                for i in range((len(indent) + 3) // 4):
                    print('%sif 1:' % (i * '    '))

                if keyword in ('else', 'elif '):
                    print('%sif 1:\n%s    pass' % (indent, indent))
                elif keyword in ('finally', 'except'):
                    print('%stry:\n%s    pass' % (indent, indent))
                print(text)
                if old_line[-1].endswith(':'):
                    print('%s    pass' % indent)

    @staticmethod
    def count(group, slen=str.__len__):
        return sum([slen(x) for x in group])

    def wrap_line(self, line, result=[]):
        """ We have a line that is too long,
            so we're going to try to wrap it.
        """

        maxlen = self.maxlen
        count = self.count
        s_lit = self.s_lit

        append = result.append

        def extend(items, start, nested, need_parens):
            for item in items:
                if len(item) > 20 and isinstance(item, s_lit):
                    item, start = item.reformat(start, nested, need_parens,
                                                maxlen, indentation)
                else:
                    start += len(item)
                append(item)
            return start

        # Extract the indentation

        indentation = line.pop(0)
        indent = len(indentation)

        # Get splittable/non-splittable groups

        dgroups = list(self.delimiter_groups(line))
        unsplittable = dgroups[::2]
        splittable = dgroups[1::2]

        # If the largest non-splittable group won't fit
        # on a line, try to add parentheses to the line.

        if max(count(x) for x in unsplittable) > maxlen - indent:
            line = self.add_parens(line, indent)
            dgroups = list(self.delimiter_groups(line))
            unsplittable = dgroups[::2]
            splittable = dgroups[1::2]

        # Deal with the first (always unsplittable) group, and
        # then set up to deal with the remainder in pairs.

        first = unsplittable[0]
        append(indentation)
        pos = extend(first, indent, False, True)
        if not splittable:
            return result
        indentation += '    '
        indent += 4
        if indent >= maxlen/2:
            maxlen = maxlen/2 + indent

        for sg, nsg in zip(splittable, unsplittable[1:]):

            if sg:
                # If we already have stuff on the line and even
                # the very first item won't fit, start a new line
                if pos > indent and pos + len(sg[0]) > maxlen:
                    append('\n')
                    append(indentation)
                    pos = indent

                # Dump lines out of the splittable group
                # until the entire thing fits
                csg = count(sg)
                need_parens = False
                while pos + csg > maxlen:
                    ready, sg = self.split_group(sg, pos, maxlen)
                    if ready[-1].endswith(' '):
                        ready[-1] = ready[-1][:-1]
                    if not need_parens:
                        need_parens = (len(ready) > 1 or
                                       sg and sg[0] != ', ')
                    pos = extend(ready, pos, True, need_parens)
                    need_parens = ready[-1] != ', '
                    append('\n')
                    append(indentation)
                    pos = indent
                    csg = count(sg)

                # Dump the remainder of the splittable group
                if sg:
                    if not need_parens:
                        need_parens = len(sg)
                    pos = extend(sg, pos, True, need_parens)

            # Dump the unsplittable group, optionally
            # preceded by a linefeed.
            cnsg = count(nsg)
            if pos > indent and pos + cnsg > maxlen:
                append('\n')
                append(indentation)
                pos = indent
            pos = extend(nsg, pos, False, True)

    def split_group(self, source, pos, maxlen):
        """ Split a group into two subgroups.  The
            first will be appended to the current
            line, the second will start the new line.

            Note that the first group must always
            contain at least one item.

            The original group may be destroyed.
        """
        first = []
        source.reverse()
        while source:
            tok = source.pop()
            first.append(tok)
            pos += len(tok)
            if source:
                tok = source[-1]
                allowed = (maxlen + 1) if tok.endswith(' ') else (maxlen - 4)
                if pos + len(tok) > allowed:
                    break

        source.reverse()
        return first, source

    def delimiter_groups(self, line, begin_delim=begin_delim,
                         end_delim=end_delim):
        """Split a line into alternating groups.
        The first group cannot have a line feed inserted,
        the next one can, etc.
        """
        text = []
        line = iter(line)
        while True:
            # First build and yield an unsplittable group
            for item in line:
                text.append(item)
                if item in begin_delim:
                    break
            if not text:
                break
            yield text

            # Now build and yield a splittable group
            level = 0
            text = []
            for item in line:
                if item in begin_delim:
                    level += 1
                elif item in end_delim:
                    level -= 1
                    if level < 0:
                        yield text
                        text = [item]
                        break
                text.append(item)
            else:
                assert not text, text
                break

    def add_parens(self, line, indent):
        """Attempt to add parentheses around the line
        in order to make it splittable.
        """

        if len(line) <= 1:
            return line

        if line[0] in self.all_statements:
            if line[0] in self.wrappable_statements:
                index = 1
                if not line[0].endswith(' '):
                    index = 2
                    assert line[1] == ' '
                line.insert(index, '(')
                if line[-1] == ':':
                    line.insert(-1, ')')
                else:
                    line.append(')')
            return line

        # That was the easy stuff.  Now for assignments and expressions
        groups = list(self.get_assign_groups(line))
        if len(groups) == 1:
            # So sad, too bad
            return ['('] + line + [')']

        counts = list(self.count(x) for x in groups)
        didwrap = False

        # If the LHS is large, wrap it first
        if sum(counts[:-1]) >= self.maxlen - indent - 4:
            for group in groups[:-1]:
                didwrap = False  # Only want to know about last group
                if len(group) > 1:
                    group.insert(0, '(')
                    group.insert(-1, ')')
                    didwrap = True

        # Might not need to wrap the RHS if wrapped the LHS
        if not didwrap or counts[-1] > self.maxlen - indent - 10:
            groups[-1].insert(0, '(')
            groups[-1].append(')')

        return [item for group in groups for item in group]

    def get_assign_groups(self, line):
        """ Split a line into groups by assignment (including
            augmented assignment)
        """
        ops = self.first_assign_ops
        next_ops = self.assign_ops
        begin_delim = self.begin_delim
        begin_end_delim = self.begin_end_delim

        group = []
        nesting = 0
        for item in line:
            group.append(item)
            if item in begin_end_delim:
                nesting += 1 if item in begin_delim else -1
            elif not nesting and item in ops:
                yield group
                group = []
                ops = next_ops
        yield group
