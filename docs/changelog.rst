=============
Release Notes
=============

0.9.0 - in development
----------------------

Bug fixes
~~~~~~~~~

* Change formatting of function and assignment type annotations to be more
  :pep:`8` friendly.
  (Contributed by Venkatesh-Prasad Ranganath in `PR 170`_.)

.. _`PR 170`: https://github.com/berkerpeksag/astor/pull/170

0.8.1 - 2019-12-10
------------------

Bug fixes
~~~~~~~~~

* Fixed precedence issue for f-string expressions that caused
  redundant parenthesis around expression.
  (Reported by Ilya Kamenshchikov in `Issue 153`_ and fixed by Batuhan Taskaya in `PR 155`_.)

.. _`Issue 153`: https://github.com/berkerpeksag/astor/issues/153
.. _`PR 155`: https://github.com/berkerpeksag/astor/pull/155

* Fixed :func:`astor.to_source` incorrectly checking whether
  *source_generator_class* is a subclass of :class:`astor.code_gen.SourceGenerator`.
  (Reported by Yu-Chia "Hank" Liu in `Issue 158`_ and fixed by Will Crichton in `PR 164`_.)

.. _`Issue 158`: https://github.com/berkerpeksag/astor/issues/158
.. _`PR 164`: https://github.com/berkerpeksag/astor/pull/164

* Fixed :exc:`TypeError` when AST nodes with unicode strings are passed to
  :func:`astor.to_source`.
  (Reported and fixed by Dominik Moritz in `PR 154`_.)

.. _`PR 154`: https://github.com/berkerpeksag/astor/pull/154

* Fixed installation issue with setuptools 41.4.0 or later due to the use of
  an undocumented feature.
  (Reported and fixed by Jonathan Ringer in `Issue 162`_ and `PR 163`_.)

.. _`Issue 162`: https://github.com/berkerpeksag/astor/issues/162
.. _`PR 163`: https://github.com/berkerpeksag/astor/pull/163

0.8.0 - 2019-05-19
------------------

New features
~~~~~~~~~~~~

* Support ``ast.Constant`` nodes being emitted by Python 3.8 (and initially
  created in Python 3.6).
  (Reported and fixed by Chris Rink in `Issue 120`_ and `PR 121`_.)

.. _`Issue 120`: https://github.com/berkerpeksag/astor/issues/120
.. _`PR 121`: https://github.com/berkerpeksag/astor/pull/121

* Support Python 3.8's assignment expressions.
  (Reported and fixed by Kodi Arfer in `Issue 126`_ and `PR 134`_.)

.. _`Issue 126`: https://github.com/berkerpeksag/astor/issues/126
.. _`PR 134`: https://github.com/berkerpeksag/astor/pull/134

* Support Python 3.8's f-string debugging syntax.
  (Reported and fixed by Batuhan Taskaya in `Issue 138`_ and `PR 139`_.)

.. _`Issue 138`: https://github.com/berkerpeksag/astor/issues/138
.. _`PR 139`: https://github.com/berkerpeksag/astor/pull/139

* :func:`astor.to_source` now has a *source_generator_class* parameter to
  customize source code generation.
  (Reported and fixed by matham in `Issue 113`_ and `PR 114`_.)

.. _`Issue 113`: https://github.com/berkerpeksag/astor/issues/113
.. _`PR 114`: https://github.com/berkerpeksag/astor/pull/114

* The :class:`~SourceGenerator` class can now be imported from the
  :mod:`astor` package directly. Previously, the ``astor.code_gen``
  submodule was needed to be imported.

* Support Python 3.8's positional only arguments. See :pep:`570` for
  more details.
  (Reported and fixed by Batuhan Taskaya in `Issue 142`_ and `PR 143`_.)

.. _`Issue 142`: https://github.com/berkerpeksag/astor/issues/142
.. _`PR 143`: https://github.com/berkerpeksag/astor/pull/143

Bug fixes
~~~~~~~~~

* Fix string parsing when there is a newline inside an f-string. (Reported by
  Adam Cécile in `Issue 119`_ and fixed by Felix Yan in `PR 123`_.)

* Fixed code generation with escaped braces in f-strings.
  (Reported by Felix Yan in `Issue 124`_ and fixed by Kodi Arfer in `PR 125`_.)

.. _`Issue 119`: https://github.com/berkerpeksag/astor/issues/119
.. _`PR 123`: https://github.com/berkerpeksag/astor/pull/123
.. _`Issue 124`: https://github.com/berkerpeksag/astor/issues/124
.. _`PR 125`: https://github.com/berkerpeksag/astor/pull/125

* Fixed code generation with attributes of integer literals, and
  with ``u``-prefixed string literals.
  (Fixed by Kodi Arfer in `PR 133`_.)

.. _`PR 133`: https://github.com/berkerpeksag/astor/pull/133

* Fixed code generation with very large integers.
  (Reported by Adam Kucz in `Issue 127`_ and fixed by Kodi Arfer in `PR 130`_.)

.. _`Issue 127`: https://github.com/berkerpeksag/astor/issues/127
.. _`PR 130`: https://github.com/berkerpeksag/astor/pull/130

* Fixed :class:`astor.tree_walk.TreeWalk` when attempting to access attributes
  created by Python's type system (such as ``__dict__`` and ``__weakref__``)
  (Reported and fixed by esupoff in `Issue 136`_ and `PR 137`_.)
  
.. _`Issue 136`: https://github.com/berkerpeksag/astor/issues/136
.. _`PR 137`: https://github.com/berkerpeksag/astor/pull/137

0.7.1 - 2018-07-06
------------------

Bug fixes
~~~~~~~~~

* Fixed installation error by adding the ``setuputils.py`` helper to the sdist.
  (Reported by Adam and fixed by Berker Peksag in `Issue 116`_.)

.. _`Issue 116`: https://github.com/berkerpeksag/astor/issues/116

0.7.0 - 2018-07-05
------------------

New features
~~~~~~~~~~~~

* Added initial support for Python 3.7.0.

  Note that if you have a subclass of ``astor.code_gen.SourceGenerator``, you
  may need to rename the keyword argument ``async`` of the following methods
  to ``is_async``:

  - ``visit_FunctionDef(..., is_async=False)``
  - ``visit_For(..., is_async=False)``
  - ``visit_With(..., is_async=False)``

  (Reported and fixed by Berker Peksag in `Issue 86`_.)

.. _`Issue 86`: https://github.com/berkerpeksag/astor/issues/86

* Dropped support for Python 2.6 and Python 3.3.

Bug fixes
~~~~~~~~~

* Fixed a bug where newlines would be inserted to a wrong place during
  printing f-strings with trailing newlines.
  (Reported by Felix Yan and contributed by Radomír Bosák in
  `Issue 89`_.)

.. _`Issue 89`: https://github.com/berkerpeksag/astor/issues/89

* Improved code generation to support ``ast.Num`` nodes containing infinities
  or NaNs.
  (Reported and fixed by Kodi Arfer in `Issue 85`_ and `Issue 100`_.)

.. _`Issue 85`: https://github.com/berkerpeksag/astor/issues/85
.. _`Issue 100`: https://github.com/berkerpeksag/astor/issues/100

* Improved code generation to support empty sets.
  (Reported and fixed by Kodi Arfer in `Issue 108`_.)

.. _`Issue 108`: https://github.com/berkerpeksag/astor/issues/108

0.6.2 - 2017-11-11
------------------

Bug fixes
~~~~~~~~~

* Restore backwards compatibility that was broken after 0.6.1.
  You can now continue to use the following pattern::

     import astor

     class SpamCodeGenerator(astor.codegen.SourceGenerator):
         ...

  (Reported by Dan Moldovan and fixed by Berker Peksag in `Issue 87`_.)

.. _`Issue 87`: https://github.com/berkerpeksag/astor/issues/87


0.6.1 - 2017-11-11
------------------

New features
~~~~~~~~~~~~

* Added ``astor.parse_file()`` as an alias to
  ``astor.code_to_ast.parsefile()``.
  (Contributed by Berker Peksag.)

Bug fixes
~~~~~~~~~

* Fix compatibility layer for the ``astor.codegen`` submodule. Importing
  ``astor.codegen`` now succeeds and raises a :exc:`DeprecationWarning`
  instead of :exc:`ImportError`.
  (Contributed by Berker Peksag.)


0.6 - 2017-10-31
----------------

New features
~~~~~~~~~~~~

* New ``astor.rtrip`` command-line tool to test round-tripping
  of Python source to AST and back to source.
  (Contributed by Patrick Maupin.)

* New pretty printer outputs much better looking code:

  - Remove parentheses where not necessary

  - Use triple-quoted strings where it makes sense

  - Add placeholder for function to do nice line wrapping on output

  (Contributed by Patrick Maupin.)

* Additional Python 3.5 support:

  - Additional unpacking generalizations (:pep:`448`)
  - Async and await (:pep:`492`)

  (Contributed by Zack M. Davis.)

* Added Python 3.6 feature support:

  - f-strings (:pep:`498`)
  - async comprehensions (:pep:`530`)
  - variable annotations (:pep:`526`)

  (Contributed by Ryan Gonzalez.)

* Code cleanup, including renaming for PEP8 and deprecation of old names.
  See :ref:`deprecations` for more information.
  (Contributed by Leonard Truong in `Issue 36`_.)

.. _`Issue 36`: https://github.com/berkerpeksag/astor/issues/36

Bug fixes
~~~~~~~~~

* Don't put trailing comma-spaces in dictionaries. astor will now create
  ``{'three': 3}`` instead of ``{'three': 3, }``.
  (Contributed by Zack M. Davis.)

* Fixed several bugs in code generation:

  #. Keyword-only arguments should come before ``**``
  #. ``from .. import <member>`` with no trailing module name did not work
  #. Support ``from .. import foo as bar`` syntax
  #. Support ``with foo: ...``, ``with foo as bar: ...`` and
     ``with foo, bar as baz: ...`` syntax
  #. Support ``1eNNNN`` syntax
  #. Support ``return (yield foo)`` syntax
  #. Support unary operations such as ``-(1) + ~(2) + +(3)``
  #. Support ``if (yield): pass``
  #. Support ``if (yield from foo): pass``
  #. ``try...finally`` block needs to come after the ``try...else`` clause
  #. Wrap integers with parentheses where applicable (e.g. ``(0).real``
     should generated)
  #. When the ``yield`` keyword is an expression rather than a statement,
     it can be a syntax error if it is not enclosed in parentheses
  #. Remove extraneous parentheses around ``yield from``

  (Contributed by Patrick Maupin in `Issue 27`_.)

.. _`Issue 27`: https://github.com/berkerpeksag/astor/issues/27


0.5 - 2015-04-18
----------------

New features
~~~~~~~~~~~~

* Added support for Python 3.5 infix matrix multiplication (:pep:`465`)
  (Contributed by Zack M. Davis.)

0.4.1 - 2015-03-15
------------------

Bug fixes
~~~~~~~~~

* Added missing ``SourceGenerator.visit_arguments()``

0.4 - 2014-06-29
----------------

New features
~~~~~~~~~~~~

* Added initial test suite and documentation

Bug fixes
~~~~~~~~~

* Added a visitor for ``NameConstant``

0.3 - 2013-12-10
----------------

New features
~~~~~~~~~~~~

* Added support for Python 3.3.

  - Added ``YieldFrom``
  - Updated ``Try`` and ``With``.

Bug fixes
~~~~~~~~~

* Fixed a packaging bug on Python 3 -- see pull requests #1 and #2 for more information.

0.2.1 -- 2012-09-20
-------------------

Enhancements
~~~~~~~~~~~~

* Modified TreeWalk to add ``_name`` suffix for functions that work on attribute names


0.2 -- 2012-09-19
-----------------

Enhancements
~~~~~~~~~~~~

* Initial Python 3 support
* Test of treewalk

0.1 -- 2012-09-19
-----------------

* Initial release
* Based on Armin Ronacher's codegen
* Several bug fixes to that and new tree walker
