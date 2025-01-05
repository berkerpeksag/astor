"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright (c) 2017 Patrick Maupin
"""

import os
import unittest

import astor.rtrip


class RtripTestCase(unittest.TestCase):

    maxDiff = None

    def test_convert_stdlib(self):
        srcdir = os.path.dirname(os.__file__)
        result = astor.rtrip.convert(srcdir, readonly=True)
        self.assertEqual([], result)


if __name__ == '__main__':
    unittest.main()
