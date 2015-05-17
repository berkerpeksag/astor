.. currentmodule:: astor

============================
astor -- AST observe/rewrite
============================

:PyPI: https://pypi.python.org/pypi/astor
:Source: https://github.com/berkerpeksag/astor
:Issues: https://github.com/berkerpeksag/astor/issues/
:License: 3-clause BSD
:Build status:
    .. image:: https://secure.travis-ci.org/berkerpeksag/astor.png
        :alt: Travis CI
        :target: https://travis-ci.org/berkerpeksag/astor/

astor is designed to allow easy manipulation of Python source via the AST.


Getting Started
---------------

Install with **pip**:

.. code-block:: bash

    $ pip install astor

or clone the latest version from GitHub_.


Features
--------

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


Functions
---------

.. note::

   This section is not done. Please look at the source code for all public
   members.


.. function:: to_source(source, indent_with=' ' * 4, \
                        add_line_information=False)

   Convert a node tree back into Python source code.

   Each level of indentation is replaced with *indent_with*. Per default this
   parameter is equal to four spaces as suggested by :pep:`8`.

   If *add_line_information* is set to ``True`` comments for the line numbers
   of the nodes are added to the output. This can be used to spot wrong line
   number information of statement nodes.

.. function:: parsefile(fname)

   Parse a python file into an AST.

   This is a very thin wrapper around ast.parse

   It does not yet handle all possible Python source
   encodings (issue #26).


.. function:: finfo(codeobj)

   Returns the file and line number of a code object.

   If the code object has a __file__ attribute (e.g. if
   it is a module), then the returned line number will be 0.


.. function:: codetoast(codeobj)

   Given a module, or a function that was compiled as part
   of a module, re-compile the module into an AST and extract
   the sub-AST for the function.  Allow caching to reduce
   number of compiles.


.. function:: striplinecol(node)

   Strip the line and column numbers from the tree
   of nodes so they do not interfere with a comparision.

.. function:: pyfiles(srctree, ignore=None)


    Recursively returns the path and filename for all
    .py files under the srctree directory.

    If ignore is not None, it will ignore any path
    that contains the ignore string.

Command line utilities
--------------------------

anti8
''''''

There is currently one command-line utility::

    python -m astor.anti8 [readonly] <srcdir>

This will create a mirror directory named tmp_anti8 and will
recursively round-trip all the Python source from the srcdir
into the tmp_anti8 dir, after compiling it and then reconstituting
it through codegen.

The purpose of anti8 is to place Python code into a canonical form --
     that just happens to be about as far away from PEP 8 as you can get.

How is this possibly useful?

Well, for a start, since it is a canonical form, you can compare the anti8
representation of a source tree against the anti8 representation of the
same tree after a PEP8 tool was run on it.

Or, maybe more importantly, after manual edits were made in the name
of PEP8.  Trust, but verify.

Note 1:
        The canonical form is only canonical for a given version of
        this module and the astor toolbox.  It is not guaranteed to
        be stable.  The only desired guarantee is that two source modules
        that parse to the same AST will be converted back into the same
        canonical form.

Note 2:
        This tool WILL TRASH the tmp_anti8 directory -- as far as it is
        concerned, it OWNS that directory.

Note 3:
        This tools WILL CRASH if you don't give it exactly one parameter
        on the command line -- the top of the tree you want to apply
        anti8 to.  You can read the traceback and figure this out, right?

Note 4:
        I lied a little bit in notes 2 and 3.  You can also pass **readonly**
        as a command line option for readonly (non-destructive mode).
        This is primarily useful for testing astor itself.


.. _GitHub: https://github.com/berkerpeksag/astor/
