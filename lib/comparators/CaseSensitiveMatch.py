# Boolean string matching.

from lib.comparators.base.comparator import Comparator


class CaseSensitiveMatch(Comparator):
    def compare(self, source, target):
        res = float(source == target)
        return res
