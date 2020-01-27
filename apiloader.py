#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import importlib

root_package = 'api'
api_dir = './' + root_package


# One-level of depth autoloader (I mean, you can define apis with
# any path you want, but don't try to create sub-folders).
# Maybe in the future I can try to generalise this and load a hierarchy of api modules
def load_api():
    # List all files, remove .py extension (and ignore __init__)
    files = [f.rsplit(".", 1)[0]
             for f in os.listdir(api_dir)
             if f.endswith('.py')
             and not f.endswith('__init__.py')
             ]

    # Dict of modules
    modules = {}
    for f in files:
        # m = importlib.import_module(api_dir + '/' + f + '.py', package=package_root + '.' + f)
        m = importlib.import_module(root_package + '.' + f)

        if hasattr(m, 'mainloop'):
            modules[m.NAME] = m.mainloop
