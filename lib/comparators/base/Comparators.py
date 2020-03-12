# Singleton that implements a Comparator factory
from lib.comparators.base.comparator import Comparator


class Comparators: # TODO: Seguir implementar singleton factory de comparators
    class __Comparators:
        def __init__(self, arg):
            self.val = arg
        def __str__(self):
            return repr(self) + self.val
    instance = None
    def __init__(self, arg):
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne(arg)
        else:
            OnlyOne.instance.val = arg
    def __getattr__(self, name):
        return getattr(self.instance, name)



# Boolean string matching. No transformations performed
class case_match(Comparator):
    def compare(self, source, target):
        res = float(source == target)
        return res


# Boolean string matching. Case-insensitive
class caseless_match(Comparator):
    def compare(self, source, target):
        res = float(source.lower() == target.lower())
        return res

