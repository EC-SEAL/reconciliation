# Singleton that implements a Comparator factory

import loader
from definitions import COMP_DIR


# Be careful with module shadowing, as I'm not checking if there
# is another module with the same name already loaded
class Comparators:
    class __Comparators:
        modules = None

        def __init__(self):
            self.modules = self.load()
            # Add the two basic builtin comparators

        def __str__(self):
            return repr(self)

        # Load the comparator modules into the factory
        def load(self):
            # Load the comparator modules and write the module names list
            return loader.load_classes(COMP_DIR, globals())

        def list(self):
            return self.modules

        def get(self, comparator_name):
            modname = comparator_name
            classname = comparator_name
            module = globals()[modname]
            class_ = getattr(module, classname)
            inst = class_()
            return inst

    instance = None

    def __init__(self):
        if not Comparators.instance:
            Comparators.instance = self.__Comparators()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def list(self):
        return self.instance.list()

    def get(self, comparator_name):
        return self.instance.get(comparator_name)
