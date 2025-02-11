"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright (c) 2017 Patrick Maupin
"""

import ast
import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from astor import to_source
from astor.node_util import dump_tree
import astor.rtrip


class RtripTestCase(unittest.TestCase):

    def test_convert_stdlib(self):
        srcdir = os.path.dirname(os.__file__)
        failed_files = astor.rtrip.convert(srcdir)

        for file_path in failed_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # Parse original source to AST
            original_ast = ast.parse(source)

            # Convert AST back to source and re-parse
            converted_source = to_source(original_ast)
            converted_ast = ast.parse(converted_source)

            # Generate detailed AST dumps for comparison
            original_dump = dump_tree(original_ast)
            converted_dump = dump_tree(converted_ast)

            # Show full AST diff on failure
            self.assertEqual(
                original_dump,
                converted_dump,
                f"AST mismatch in file: {file_path}\n"
                f"Generated code:\n{converted_source}"
            )

        # Final assertion to ensure the failed_files list is empty
        self.assertEqual(failed_files, [], "Files failed to round-trip")


if __name__ == '__main__':
    unittest.main()
