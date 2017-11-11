import importlib
import sys


def _save_and_remove_module(name, orig_modules):
    """Helper function to save and remove a module from sys.modules
    Raise ImportError if the module can't be imported.
    """
    # try to import the module and raise an error if it can't be imported
    if name not in sys.modules:
        __import__(name)
        del sys.modules[name]
    for modname in list(sys.modules):
        if modname == name or modname.startswith(name + '.'):
            orig_modules[modname] = sys.modules[modname]
            del sys.modules[modname]


def import_fresh_module(name, fresh=(), blocked=()):
    """Import and return a module, deliberately bypassing sys.modules.

    This function imports and returns a fresh copy of the named Python module
    by removing the named module from sys.modules before doing the import.
    Note that unlike reload, the original module is not affected by
    this operation.
    """
    orig_modules = {}
    names_to_remove = []
    _save_and_remove_module(name, orig_modules)
    try:
        for fresh_name in fresh:
            _save_and_remove_module(fresh_name, orig_modules)
        for blocked_name in blocked:
            if not _save_and_block_module(blocked_name, orig_modules):
                names_to_remove.append(blocked_name)
        fresh_module = importlib.import_module(name)
    except ImportError:
        fresh_module = None
    finally:
        for orig_name, module in orig_modules.items():
            sys.modules[orig_name] = module
        for name_to_remove in names_to_remove:
            del sys.modules[name_to_remove]
    return fresh_module
