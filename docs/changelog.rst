Release Notes
-------------


0.6 - Work in Progress
-------------------------

New features
~~~~~~~~~~~~

* New ``astor.rtrip`` submodule and doc

* New pretty printer outputs much better looking code

* Significant codebase refactoring
  - Much easier to add new node types
  - Much easier to handle precedence issues
  - Main flow easier to follow in tree

* Additional Python 3.5 support:
  - New starargs and kwargs support
  - Async and await

* Added Python 3.6 feature support:

  - f-strings
  - async comprehensions
  - variable annotations

* Updated test infrastructure and documentation
* Code cleanup, including renaming for PEP8 and deprecation of old names

Bug fixes
~~~~~~~~~

* TODO:  Check issues...

0.5 - 2015-04-18
-------------------------

New features
~~~~~~~~~~~~

* Added support for Python 3.5 infix matrix multiplication

0.4.1 - 2015-03-15
-------------------------

Bug fixes
~~~~~~~~~~

* Added missing ``SourceGenerator.visit_arguments()``

0.4 - 2014-06-29
-------------------------

New features
~~~~~~~~~~~~

* Added initial test suite and documentation

Bug fixes
~~~~~~~~~~

* Added a visitor for ``NameConstant``

0.3 - 2013-12-10
-------------------------

New features
~~~~~~~~~~~~

* Added support for Python 3.3.

  - Added ``YieldFrom``
  - Updated ``Try`` and ``With``.

Bug fixes
~~~~~~~~~~

* Fixed a packaging bug on Python 3 -- see pull requests #1 and #2 for more information.

0.2.1 -- 2012-09-20
------------------------

Enhancements
~~~~~~~~~~~~~

* Modified TreeWalk to add ``_name`` suffix for functions that work on attribute names


0.2 -- 2012-09-19
------------------------

Enhancements
~~~~~~~~~~~~~

* Initial Python 3 support
* Test of treewalk

0.1 -- 2012-09-19
------------------------

* Initial release
* Based on Armin Ronacher's codegen
* Several bug fixes to that and new tree walker
