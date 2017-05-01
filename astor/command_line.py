# -*- coding: utf-8 -*-
"""
License: 3-clause BSD

Copyright 2017 (c) Patrick Maupin

This supports subcommands by importing every sibling
submodule, and letting them call `add_command` to
register themselves.

The main document string should have a header and
a footer, separated by '----\n'
"""

import sys
import os

# Each submodule can place its commands here, indexed
# by command name
subcommands = {}
fixed_path = False


class OneCommand(str):
    """ OneCommand subclasses string for easy sorting.
        The string should be something that indicates
        how it should be sorted for display.  Perhaps
        the command name; perhaps something else.

        Attributes of the class should be:

            - cmd -- what to type to invoke this
            - shorthelp -- help for global printout
            - invoke() -- method to invoke command
    """


def add_command(name, invoke, shorthelp, sortname=None):
    cmd = OneCommand(sortname or name)
    cmd.cmd = name
    cmd.shorthelp = shorthelp
    cmd.invoke = invoke
    subcommands[name] = cmd


def main(args=sys.argv):
    # Make sure we've been imported properly
    if __name__ == '__main__':
        from .command_line import main
        return main(args)

    # Let all command line utilities register
    for fname in os.listdir(os.path.dirname(__file__)):
        if fname.endswith('.py') and not fname.startswith('__'):
            __import__(fname[:-3], globals(), locals(), [], 1)

    add_command('cprofile', do_profile, """
        cprofile may be inserted in front of other commands in order
        to do profiling.
""", 'zzzz')

    add_command('help', do_help, """
        help may be used to provide help on sub-commands.
""")

    # Remove extraneous cruft from start of args for display
    global fixed_path
    if args is sys.argv and not fixed_path:
        fixed_path = True
        fullname = __name__
        if fullname.replace('.', os.sep) in args[0]:
            args[0] = fullname
        else:
            args[0] = fullname.rsplit('.', 1)[0]

    # Find first possible command
    cmds = set(subcommands) & set(args[1:])
    if not cmds:
        return main_help(args)

    # Invoke the subcommand
    cmd = sorted(((args.index(x), x) for x in cmds))[0][-1]
    args.remove(cmd)
    args[0] = '%s %s' % (args[0], cmd)
    subcommands[cmd].invoke(args)


def do_profile(args):
    try:
        import cProfile
    except ImportError:
        import profile as cProfile
    cProfile.run('main()')


def do_help(args):
    if len(args) > 1:
        args.append('-h')
        args[0] = args[0].replace(' help', '')
        return main(args)
    main_help(args)


def main_help(args):
    from . import __doc__ as doc
    name = args[0]
    args = args[1:]
    header, footer = normstring(doc).split('----\n')
    print(header.rstrip('\n'))
    if set(args) - set('-h --help'.split()):
        print('\nUnknown command: %s' % ' '.join(args))

    if subcommands:
        print('\nAvailable subcommands:')
        for cmd in sorted(subcommands.values()):
            print('\n    %s %s:\n%s' % (name, cmd.cmd, cmd.shorthelp))
    print(footer)


def normstring(s):
    return s.replace('\r\n', '\n').replace('\r', '\n')


if __name__ == '__main__':
    main()
