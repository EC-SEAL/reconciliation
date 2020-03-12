# Boolean string matching. Case-insensitive

from lib.comparators.base.comparator import Comparator


class CaseInsensitiveMatch(Comparator):
    def compare(self, source, target):
        res = float(source.lower() == target.lower())
        return res
