#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import os
import re
import sys
import importlib


# One-level of depth autoloader (I mean, you can define apis with
# any path you want, but don't try to create sub-folders).
# Maybe in the future I can try to generalise this and load a hierarchy of api modules
def load_libs(source_directory, root_package_name):
    logging.info("Loading package " + root_package_name + " from " + source_directory)
    # List all files, remove .py extension (and ignore __init__)
    files = [f.rsplit(".", 1)[0]
             for f in os.listdir(source_directory)
             if f.endswith('.py')
             and not f.endswith('__init__.py')
             ]
    modules = set()
    for f in files:
        # m = importlib.import_module(api_dir + '/' + f + '.py', package=package_root + '.' + f)
        m = importlib.import_module(root_package_name + '.' + f)
    return list(modules)


# The above autoloader does not work for modules including classes we want
# to instantiate. 'env' should always be a call to globals(), but it must be
# the environment at the caller function, can't be called inside here
#  Usage example:
#    mods = loader.load_classes(ROOT_DIR+"/"+"lib"+"/"+"comparators", globals())
#    modname = "damerauLevenshtein" #(or mods[n])
#    classname = "damerauLevenshtein" #(or mods[n])
#    module = globals()[modname]
#    class_ = getattr(module, classname)
#    inst = class_()
def load_classes(path, env):
    sys.path.append(path)
    mods = _list_modules(path)
    for module_name in mods:
        env[module_name] = __import__(module_name)
    return mods


def _list_modules(path):
    mods = set()
    for entry in os.listdir(path):
        if os.path.isfile(os.path.join(path, entry)):
            is_python_file = re.search("(.+)\\.py$", entry)
            if is_python_file:
                mods.add(is_python_file.groups()[0])
    return mods
