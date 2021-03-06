# Singleton that implements a Comparator factory

from definitions import COMP_DIR

from lib.Factory import Factory


# Be careful with module shadowing, as I'm not checking if there
# is another module with the same name already loaded
class Comparators:
    instance = None

    def __init__(self):
        if not Comparators.instance:
            Comparators.instance = Factory(COMP_DIR)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def list(self):
        return self.instance.list()

    def get(self, comparator_name):
        return self.instance.get(comparator_name)
