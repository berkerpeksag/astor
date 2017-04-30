"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright (c) 2014 Berker Peksag
Copyright (c) 2015, 2017 Patrick Maupin

Shows an example of subclassing of SourceGenerator
to insert comment nodes.

"""

import ast

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from test_code_gen import canonical
except ImportError:
    from .test_code_gen import canonical

from astor.code_gen import SourceGenerator


class CommentCode(object):
    """  Represents commented out code.
    """
    def __init__(self, subnode):
        self.subnode = subnode


class BlockComment(object):
    """  Represents a block comment.
    """
    def __init__(self, text):
        self.text = text


class SourceWithComments(SourceGenerator):
    """ Subclass the SourceGenerator and add our node.
        When our node is visited, write the underlying node,
        and then go back and comment it.
    """

    def visit_CommentCode(self, node):
        statements = self.statements
        index = len(statements)
        self.write(node.subnode)
        for index in range(index, len(statements)):
            mylist = statements[index]
            if mylist[0].startswith('\n'):
                continue
            mylist[0] = '#' + mylist[0]

    def visit_BlockComment(self, node):
        """ Print a block comment.  This currently
            handles a single line, but it could be beefed
            up to handle more, or even consolidated into
            a single visit_Comment class with the CommentCode
            visitor, and make decisions based on the type
            of the node.
        """
        self.statement(node, '# ', node.text)


class SubclassCodegenCase(unittest.TestCase):

    def test_comment_node(self):
        """ Strip the comments out of this source, then
            try to regenerate them.
        """

        source = canonical("""
            if 1:

                def sam(a, b, c):
                    # This is a block comment
                    x, y, z = a, b, c

            #    def bill(a, b, c):
            #        x, y, z = a, b, c

                def mary(a, b, c):
                    x, y, z = a, b, c
        """)

        # Strip the block comment
        uncommented_src = source.replace('        #'
                                         ' This is a block comment\n', '')

        # Uncomment the bill function and generate the AST
        uncommented_src = uncommented_src.replace('#', '')
        ast1 = ast.parse(uncommented_src)

        # Modify the AST to comment out the bill function
        ast1.body[0].body[1] = CommentCode(ast1.body[0].body[1])

        # Add a comment under sam
        ast1.body[0].body[0].body.insert(0, BlockComment(
                                         "This is a block comment"))
        # Assert it round-trips OK
        dest = canonical(SourceWithComments.to_source(ast1))
        self.assertEqual(source, dest)


if __name__ == '__main__':
    unittest.main()
