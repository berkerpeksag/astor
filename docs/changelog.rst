Release Notes
-------------

======= ======================================================================================
Version Changes
======= ======================================================================================
0.1     Initial release
0.2     Added Python 3 support
0.2.1   Modified TreeWalk to add ``_name`` suffix for functions that work on attribute names
0.3     | Added support for Python 3.3. Added ``YieldFrom`` and updated ``Try`` and ``With``.
        | Fixed a packaging bug on Python 3. See pull requests #1 and #2 for more information.
0.4     | Added a visitor for ``NameConstant``.
        | Added initial test suite and documentation.
0.4.1   Added missing ``SourceGenerator.visit_arguments()``
0.5     Added support for Python 3.5 infix matrix multiplication
0.6     | Added support for Python 3.6 f-strings and async comprehensions.
        | Deprecation warnings:
        |   Old         -> New
        |   get_boolop  -> get_op_symbol
        |   get_binop   -> get_op_symbol
        |   get_cmpop   -> get_op_symbol
        |   get_unaryop -> get_op_symbol
        |   get_anyop   -> get_op_symbol
        |   parsefile   -> code_to_ast.parse_file
        |   codetoast   -> code_to_ast
        |   dump        -> dump_tree
        |   all_symbols -> symbol_data
        |   treewalk    -> tree_walk
        |   codegen     -> code_gen
        | Old functions will be removed in 0.7
======= ======================================================================================
