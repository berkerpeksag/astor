import ast
import textwrap

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

    def test_json_to_ast_with_class_with_attribute(self):
        ast_dict = {
            "ast_type": "Module",
            "body": [
                {
                    "ast_type": "ClassDef",
                    "bases": [],
                    "body": [
                        {
                            "args": {
                                "args": [
                                    {
                                        "annotation": None,
                                        "arg": "self",
                                        "ast_type": "arg",
                                        "col_offset": 17,
                                        "lineno": 3,
                                    },
                                    {
                                        "annotation": None,
                                        "arg": "x",
                                        "ast_type": "arg",
                                        "col_offset": 23,
                                        "lineno": 3,
                                    },
                                ],
                                "ast_type": "arguments",
                                "defaults": [],
                                "kw_defaults": [],
                                "kwarg": None,
                                "kwonlyargs": [],
                                "vararg": None,
                            },
                            "ast_type": "FunctionDef",
                            "body": [
                                {
                                    "ast_type": "Assign",
                                    "col_offset": 8,
                                    "lineno": 4,
                                    "targets": [
                                        {
                                            "ast_type": "Attribute",
                                            "attr": "x",
                                            "col_offset": 8,
                                            "ctx": {"ast_type": "Store"},
                                            "lineno": 4,
                                            "value": {
                                                "ast_type": "Name",
                                                "col_offset": 8,
                                                "ctx": {"ast_type": "Load"},
                                                "id": "self",
                                                "lineno": 4,
                                            },
                                        }
                                    ],
                                    "value": {
                                        "ast_type": "Name",
                                        "col_offset": 17,
                                        "ctx": {"ast_type": "Load"},
                                        "id": "x",
                                        "lineno": 4,
                                    },
                                }
                            ],
                            "col_offset": 4,
                            "decorator_list": [],
                            "lineno": 3,
                            "name": "__init__",
                            "returns": None,
                        }
                    ],
                    "col_offset": 0,
                    "decorator_list": [],
                    "keywords": [],
                    "lineno": 2,
                    "name": "Test",
                }
            ],
        }

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))
        expected_ast = astor.dump_tree(
            ast.parse(
                textwrap.dedent(
                    """
            class Test:
                def __init__(self, x):
                    self.x = x
        """
                )
            )
        )

        self.assertEqual(result_ast, expected_ast)

    def test_json_to_ast_with_dictionary(self):
        ast_dict = {
            "ast_type": "Module",
            "body": [
                {
                    "ast_type": "Expr",
                    "col_offset": 0,
                    "lineno": 2,
                    "value": {
                        "ast_type": "Dict",
                        "col_offset": 0,
                        "keys": [
                            {
                                "ast_type": "Str",
                                "col_offset": 4,
                                "lineno": 3,
                                "s": "string",
                            },
                            {
                                "ast_type": "Str",
                                "col_offset": 4,
                                "lineno": 4,
                                "s": "int",
                            },
                            {
                                "ast_type": "Str",
                                "col_offset": 4,
                                "lineno": 5,
                                "s": "float",
                            },
                            {
                                "ast_type": "Str",
                                "col_offset": 4,
                                "lineno": 6,
                                "s": "boolean",
                            },
                            {
                                "ast_type": "Str",
                                "col_offset": 4,
                                "lineno": 7,
                                "s": "null",
                            },
                            {
                                "ast_type": "Str",
                                "col_offset": 4,
                                "lineno": 8,
                                "s": "dict",
                            },
                        ],
                        "lineno": 2,
                        "values": [
                            {
                                "ast_type": "Str",
                                "col_offset": 14,
                                "lineno": 3,
                                "s": "A string",
                            },
                            {
                                "ast_type": "Num",
                                "col_offset": 11,
                                "lineno": 4,
                                "n": {"ast_type": "int", "n": 42},
                            },
                            {
                                "ast_type": "Num",
                                "col_offset": 13,
                                "lineno": 5,
                                "n": {"ast_type": "float", "n": 3.14},
                            },
                            {
                                "ast_type": "NameConstant",
                                "col_offset": 15,
                                "lineno": 6,
                                "value": True,
                            },
                            {
                                "ast_type": "NameConstant",
                                "col_offset": 12,
                                "lineno": 7,
                                "value": None,
                            },
                            {
                                "ast_type": "Dict",
                                "col_offset": 12,
                                "keys": [],
                                "lineno": 8,
                                "values": [],
                            },
                        ],
                    },
                }
            ],
        }

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))
        expected_ast = astor.dump_tree(
            ast.parse(
                textwrap.dedent(
                    """
           {
                "string": "A string",
                "int": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "dict": {}
            }
        """
                )
            )
        )

        # self.assertEqual(result_ast, expected_ast)
        assert result_ast == expected_ast


if __name__ == "__main__":
    unittest.main()
