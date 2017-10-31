=============
Release Notes
=============

0.6 - Work in Progress
----------------------

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
    (Contributed by Zack M. Davis.)

  - Async and await (:pep:`492`)
    (Contributed by Zack M. Davis.)

* Added Python 3.6 feature support:

  - f-strings (:pep:`498`)
  - async comprehensions (:pep:`530`)
  - variable annotations (:pep:`526`

  (Contributed by Ryan Gonzalez.)

* Code cleanup, including renaming for PEP8 and deprecation of old names.
  See :ref:`deprecations` for more information.
  (Contributed by Leonard Truong in issue #36.)

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

  (Contributed by Patrick Maupin in issue 27.)

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
