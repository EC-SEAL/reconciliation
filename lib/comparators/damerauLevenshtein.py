import textdistance

from lib.comparators.base.comparator import Comparator


# Approximate string matching. Levenshtein Distance with transposition
class damerauLevenshtein(Comparator):
    def compare(self, source, target):
        res = textdistance.damerau_levenshtein.normalized_similarity(source, target)
        return res
