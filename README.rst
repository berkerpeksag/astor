=============================
astor -- AST observe/rewrite
=============================

astor is designed to allow easy manipulation of Python source via the AST.

There are some other similar libraries, but astor focuses on the following areas:

  - Round-trip back to Python via Armin Ronacher's codegen.py module:

      - Modified AST doesn't need linenumbers, ctx, etc. or otherwise be directly compileable
      - Easy to read generated code as, well, code

  - dump pretty-printing of AST

      - Harder to read than round-tripped code, but more accurate to figure out what
        is going on.

      - Easier to read than dump from built-in AST module

  - Non-recursive treewalk

      - Sometimes you want a recursive treewalk (and astor supports that, starting
        at any node on the tree), but sometimes you don't need to do that.  astor
        doesn't require you to explicitly visit sub-nodes unless you want to:

          - You can add code that executes before a node's children are visited, and/or
          - You can add code that executes after a node's children are visited, and/or
          - You can add code that executes and keeps the node's children from being
            visited (and optionally visit them yourself via a recursive call)

      - Write functions to access the tree based on object names and/or attribute names
      - Enjoy easy access to parent node(s) for tree rewriting
