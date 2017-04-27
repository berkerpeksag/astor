"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright (c) 2017 Patrick Maupin
"""

import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor.rtrip


class RtripTestCase(unittest.TestCase):

    def test_convert_stdlib(self):
        srcdir = os.path.dirname(os.__file__)
        result = astor.rtrip.convert(srcdir)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
