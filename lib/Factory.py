# Generic Factory implementation

import loader


# Be careful with module shadowing, as I'm not checking if there
# is another module with the same name already loaded
class Factory:
    modules = None
    load_path = None

    def __init__(self, load_path):
        self.load_path = load_path
        self.modules = self.load()

    def __str__(self):
        return repr(self)

    # Load the comparator modules into the factory
    def load(self):
        # Load the comparator modules and write the module names list
        return loader.load_classes(self.load_path, globals())

    def list(self):
        return self.modules

    def get(self, comparator_name):
        modname = comparator_name
        classname = comparator_name
        module = globals()[modname]
        class_ = getattr(module, classname)
        inst = class_()
        return inst
