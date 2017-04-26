"""
Part of the astor library for Python AST manipulation

License: 3-clause BSD

Copyright (c) 2014 Berker Peksag
Copyright (c) 2015, 2017 Patrick Maupin

Use this by putting a link to astunparse's common.py test file.

"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from test_code_gen import Comparisons
except ImportError:
    from .test_code_gen import Comparisons

try:
    from astunparse_common import AstunparseCommonTestCase
except ImportError:
    AstunparseCommonTestCase = None

if AstunparseCommonTestCase is not None:

    class UnparseTestCase(AstunparseCommonTestCase, unittest.TestCase,
                          Comparisons):
    
        def check_roundtrip(self, code1, mode=None):
            self.assertAstRoundtrips(code1)

        def test_files(self):
            """ Don't bother -- we do this manually and more thoroughly """

if __name__ == '__main__':
    unittest.main()
