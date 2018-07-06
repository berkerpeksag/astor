..
  **************************************************************
  Note that his file was designed to be viewed at Read the Docs.
  Some content will not display properly when viewing using the
  GitHub browser.
  **************************************************************

.. currentmodule:: astor

############################
astor -- AST observe/rewrite
############################

:PyPI: https://pypi.org/project/astor/
:Source: https://github.com/berkerpeksag/astor
:Issues: https://github.com/berkerpeksag/astor/issues/
:License: 3-clause BSD
:Build status:
    .. image:: https://secure.travis-ci.org/berkerpeksag/astor.svg
        :alt: Travis CI
        :target: https://travis-ci.org/berkerpeksag/astor/


.. toctree::
   :hidden:

   self
   changelog


astor is designed to allow easy manipulation of Python source via the AST.

***************
Getting Started
***************

Install with **pip**:

.. code-block:: bash

    $ pip install astor

or clone the latest version from GitHub_.


********
Features
********

There are some other similar libraries, but astor focuses on the following
areas:

- Round-trip back to Python via Armin Ronacher's codegen.py module:

  - Modified AST doesn't need linenumbers, ctx, etc. or otherwise be directly
    compileable
  - Easy to read generated code as, well, code

- Dump pretty-printing of AST

  - Harder to read than round-tripped code, but more accurate to figure out what
    is going on.

  - Easier to read than dump from built-in AST module

- Non-recursive treewalk

  - Sometimes you want a recursive treewalk (and astor supports that, starting
    at any node on the tree), but sometimes you don't need to do that. astor
    doesn't require you to explicitly visit sub-nodes unless you want to:

  - You can add code that executes before a node's children are visited, and/or
  - You can add code that executes after a node's children are visited, and/or
  - You can add code that executes and keeps the node's children from being
    visited (and optionally visit them yourself via a recursive call)

  - Write functions to access the tree based on object names and/or attribute
    names
  - Enjoy easy access to parent node(s) for tree rewriting

.. _deprecations:

************
Deprecations
************

.. versionadded:: 0.6

Modules
~~~~~~~

===================  ====================
astor 0.5            astor 0.6+
===================  ====================
``astor.codegen``    ``astor.code_gen``
``astor.misc``       ``astor.file_util``
``astor.treewalk``   ``astor.tree_walk``
===================  ====================

Functions
~~~~~~~~~

========================  ====================
astor 0.5                 astor 0.6+
========================  ====================
``astor.codetoast()``     ``astor.code_to_ast()``
``astor.parsefile()``     ``astor.parse_file()``
``astor.dump()``          ``astor.dump_tree()``
``astor.get_anyop()``     ``astor.get_op_symbol()``
``astor.get_boolop()``    ``astor.get_op_symbol()``
``astor.get_binop()``     ``astor.get_op_symbol()``
``astor.get_cmpop()``     ``astor.get_op_symbol()``
``astor.get_unaryop()``   ``astor.get_op_symbol()``
========================  ====================

Attributes
~~~~~~~~~~

========================  ====================
astor 0.5                 astor 0.6+
========================  ====================
``astor.codetoast``       ``astor.code_to_ast``
``astor.all_symbols``     ``astor.symbol_data``
========================  ====================


*********
Functions
*********

.. function:: to_source(source, indent_with=' ' * 4, \
                        add_line_information=False)

    Convert a node tree back into Python source code.

    Each level of indentation is replaced with *indent_with*. Per default this
    parameter is equal to four spaces as suggested by :pep:`8`.

    If *add_line_information* is set to ``True`` comments for the line numbers
    of the nodes are added to the output. This can be used to spot wrong line
    number information of statement nodes.

.. function:: codetoast
.. function:: code_to_ast(codeobj)

    Given a module, or a function that was compiled as part
    of a module, re-compile the module into an AST and extract
    the sub-AST for the function.  Allow caching to reduce
    number of compiles.

    .. deprecated:: 0.6
       ``codetoast()`` is deprecated.


.. function:: astor.parsefile
.. function:: astor.parse_file
.. function:: astor.code_to_ast.parse_file(fname)

    Parse a Python file into an AST.

    This is a very thin wrapper around :func:`ast.parse`.

    .. deprecated:: 0.6
       ``astor.parsefile()`` is deprecated.

    .. versionadded:: 0.6.1
       Added the ``astor.parse_file()`` function as an alias.

.. function:: astor.code_to_ast.get_file_info(codeobj)

    Returns the file and line number of *codeobj*.

    If *codeobj* has a ``__file__`` attribute (e.g. if
    it is a module), then the returned line number will be 0.

    .. versionadded:: 0.6


.. function:: astor.code_to_ast.find_py_files(srctree, ignore=None)

    Recursively returns the path and filename for all
    Python files under the *srctree* directory.

    If *ignore* is not ``None``, it will ignore any path
    that contains the ignore string.

    .. versionadded:: 0.6


.. function:: iter_node(node, unknown=None)

    This function iterates over an AST node object:

    - If the object has a _fields attribute,
      it gets attributes in the order of this
      and returns name, value pairs.

    - Otherwise, if the object is a list instance,
      it returns name, value pairs for each item
      in the list, where the name is passed into
      this function (defaults to blank).

    - Can update an unknown set with information about
      attributes that do not exist in fields.


.. function:: dump
.. function:: dump_tree(node, name=None, initial_indent='', \
                        indentation='    ', maxline=120, maxmerged=80)

    This function pretty prints an AST or similar structure
    with indentation.

    .. deprecated:: 0.6
       ``astor.dump()`` is deprecated.


.. function:: strip_tree(node)

    This function recursively removes all attributes from
    an AST tree that are not referenced by the _fields member.

    Returns a set of the names of all attributes stripped.
    By default, this should just be the line number and column.

    This canonicalizes two trees for comparison purposes.

    .. versionadded:: 0.6


.. function:: get_boolop
.. function:: get_binop
.. function:: get_cmpop
.. function:: get_unaryop
.. function:: get_anyop
.. function:: get_op_symbol(node, fmt='%s')

    Given an ast node, returns the string representing the
    corresponding symbol.

    .. deprecated:: 0.6
       ``get_boolop()``, ``get_binop()``, ``get_cmpop()``, ``get_unaryop()``
       and ``get_anyop()`` functions are deprecated.


*******
Classes
*******

.. class:: file_util.CodeToAst

    This is the base class for the helper function :func:`code_to_ast`.
    It may be subclassed, but probably will not need to be.


.. class:: tree_walk.TreeWalk(node=None)

    The ``TreeWalk`` class is designed to be subclassed in order
    to walk a tree in arbitrary fashion.


.. class:: node_util.ExplicitNodeVisitor

    The ``ExplicitNodeVisitor`` class subclasses the :class:`ast.NodeVisitor`
    class, and removes the ability to perform implicit visits.
    This allows for rapid failure when your code encounters a
    tree with a node type it was not expecting.


**********************
Command-line utilities
**********************

There is currently one command-line utility:

rtrip
~~~~~

.. versionadded:: 0.6

::

    python -m astor.rtrip [readonly] [<source>]

This utility tests round-tripping of Python source to AST
and back to source.

.. warning::
   This tool **will trash** the *tmp_rtrip* directory unless
   the *readonly* option is specified.

If readonly is specified, then the source will be tested,
but no files will be written.

if the source is specified to be "stdin" (without quotes)
then any source entered at the command line will be compiled
into an AST, converted back to text, and then compiled to
an AST again, and the results will be displayed to stdout.

If neither readonly nor stdin is specified, then rtrip
will create a mirror directory named tmp_rtrip and will
recursively round-trip all the Python source from the source
into the tmp_rtrip dir, after compiling it and then reconstituting
it through code_gen.to_source.

If the source is not specified, the entire Python library will be used.

The purpose of rtrip is to place Python code into a canonical form.

This is useful both for functional testing of astor, and for
validating code edits.

For example, if you make manual edits for PEP8 compliance,
you can diff the rtrip output of the original code against
the rtrip output of the edited code, to insure that you
didn't make any functional changes.

For testing astor itself, it is useful to point to a big codebase,
e.g::

    python -m astor.rtrip

to round-trip the standard library.

If any round-tripped files fail to be built or to match, the
tmp_rtrip directory will also contain fname.srcdmp and fname.dstdmp,
which are textual representations of the ASTs.


.. note::
   The canonical form is only canonical for a given version of
   this module and the astor toolbox.  It is not guaranteed to
   be stable.  The only desired guarantee is that two source modules
   that parse to the same AST will be converted back into the same
   canonical form.

.. _GitHub: https://github.com/berkerpeksag/astor/
