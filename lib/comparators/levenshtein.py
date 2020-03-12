import textdistance

from lib.comparators.base.comparator import Comparator

# Approximate string matching. Levenshtein Distance
class levenshtein(Comparator):
    def compare(self, source, target):
        res = textdistance.levenshtein.normalized_similarity(source, target)
        return res
