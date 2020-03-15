# Singleton that implements a Processor factory

from definitions import PROC_DIR

from lib.Factory import Factory


# Be careful with module shadowing, as I'm not checking if there
# is another module with the same name already loaded
class Processors:
    instance = None

    def __init__(self):
        if not Processors.instance:
            Processors.instance = Factory(PROC_DIR)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def list(self):
        return self.instance.list()

    def get(self, processor_name):
        return self.instance.get(processor_name)
