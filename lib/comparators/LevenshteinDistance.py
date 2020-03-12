import textdistance

from lib.comparators.base.comparator import Comparator


# Approximate string matching. Levenshtein Distance (Be careful with naming or you will override other libs)
class LevenshteinDistance(Comparator):
    def compare(self, source, target):
        res = textdistance.levenshtein.normalized_similarity(source, target)
        return res
