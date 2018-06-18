import ast

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


class JsonToCodeTestCase(unittest.TestCase):
    def test_json_to_ast(self):
        ast_dict = {
            "ast_type": "Module",
            "body": [
                {
                    "ast_type": "Assign",
                    "targets": [
                        {
                            "ast_type": "Name",
                            "id": "x",
                            "ctx": {"ast_type": "Store"},
                            "lineno": 1,
                            "col_offset": 0,
                        }
                    ],
                    "value": {
                        "ast_type": "Num",
                        "n": {"ast_type": "int", "n": 42},
                        "lineno": 1,
                        "col_offset": 2,
                    },
                    "lineno": 1,
                    "col_offset": 0,
                }
            ],
        }

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))
        expected_ast = astor.dump_tree(ast.parse("x = 42"))

        self.assertEqual(result_ast, expected_ast)

    def test_json_to_ast_with_javascript_integer_fix(self):
        ast_dict = {
            "ast_type": "Module",
            "body": [
                {
                    "ast_type": "Assign",
                    "targets": [
                        {
                            "ast_type": "Name",
                            "id": "x",
                            "ctx": {"ast_type": "Store"},
                            "lineno": 1,
                            "col_offset": 0,
                        }
                    ],
                    "value": {
                        "ast_type": "Num",
                        "n": {
                            "ast_type": "int",
                            "n": 18446744073709551616,
                            "n_str": "18446744073709551616",
                        },
                        "lineno": 1,
                        "col_offset": 2,
                    },
                    "lineno": 1,
                    "col_offset": 0,
                }
            ],
        }

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))
        expected_ast = astor.dump_tree(ast.parse("x = 18446744073709551616"))

        self.assertEqual(result_ast, expected_ast)


if __name__ == "__main__":
    unittest.main()
