import ast
import json
import os
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import astor


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

PYTHON_VERSION = sys.version_info[:2]


class JsonToCodeTestCase(unittest.TestCase):
    def test_json_to_ast(self):
        with open(os.path.join(FIXTURE_DIR, "integer.json")) as f:
            ast_dict = json.load(f)

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))

        with open(os.path.join(FIXTURE_DIR, "integer.py")) as f:
            expected_ast = astor.dump_tree(ast.parse(f.read()))

        assert result_ast == expected_ast

    def test_json_to_ast_with_javascript_integer_fix(self):
        with open(os.path.join(FIXTURE_DIR, "integer_javascript.json")) as f:
            ast_dict = json.load(f)

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))

        with open(os.path.join(FIXTURE_DIR, "integer_javascript.py")) as f:
            expected_ast = astor.dump_tree(ast.parse(f.read()))

        assert result_ast == expected_ast

    def test_json_to_ast_with_class_with_attribute(self):
        if PYTHON_VERSION < (3,):
            version = "27"
        elif PYTHON_VERSION < (3, 6):
            version = "34"
        else:
            version = "36"

        json_filename = "class_with_attribute.py{}.json".format(version)

        with open(os.path.join(FIXTURE_DIR, json_filename)) as f:
            ast_dict = json.load(f)

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))

        with open(os.path.join(FIXTURE_DIR, "class_with_attribute.py")) as f:
            expected_ast = astor.dump_tree(ast.parse(f.read()))

        assert result_ast == expected_ast

    def test_json_to_ast_with_dictionary(self):
        version = "2" if PYTHON_VERSION < (3,) else "3"
        json_filename = "dictionary.py{}.json".format(version)

        with open(os.path.join(FIXTURE_DIR, json_filename)) as f:
            ast_dict = json.load(f)

        result_ast = astor.dump_tree(astor.json_to_ast(ast_dict))

        with open(os.path.join(FIXTURE_DIR, "dictionary.py")) as f:
            expected_ast = astor.dump_tree(ast.parse(f.read()))

        assert result_ast == expected_ast


if __name__ == "__main__":
    unittest.main()
