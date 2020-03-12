#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Factory for the different comparison methods for a pair of strings
# Supports library loading of additional comparators
# Classes must implement:
#    def compare(self, source, target):
# Receive 2 strings, return a string similarity rate between 0 and 1


import loader
from lib.comparators.base.comparator import Comparator
from definitions import COMP_DIR, COMP_ROOT_PACKAGE


# Base comparator list. It will be extended on runtime with the comparator libraries


# Load the comparator modules, and export a global variable for listing them
def load_comparators():
    global comparator_list
    # Load the comparator modules
    mods = loader.load_libs(COMP_DIR, COMP_ROOT_PACKAGE)
    # Merge both lists
    comparator_list = comparator_list + mods
    # Remove possible duplicates
    comparator_list = list(dict.fromkeys(comparator_list))


class Comparison:

    def __init__(self):
        self.comparator = case_match()
        self.comparator_list = []
        self._load_comparators()

    def list_comparators(self):
        return self.comparator_list

    # Pass a comparator class name
    def set_comparator(self, comparator):
        compare_op = getattr(comparator, "compare", None)
        if not callable(compare_op):
            raise BadClassInterface("Passed object of class " + comparator.__class__ + " does not implement 'compare'")
        self.comparator = comparator()

    def compare(self, source, target):
        return self.comparator.compare(source, target)


class BadClassInterface(Exception):
    def __init__(self, message):
        self.message = message

# TODO: improve algorithm
# jaro-winkler -- NIKOS USES THIS ONE (with 0.7 threshold) AND THE LD (with distance <4) limits distance
#   of transpositions to half the length, awards to ordered substring, so not good for multiple transpositions
# Strcmp95 -- this is the original jaro-winkler impl. Why does it appear twice?
# LCS - no acepta sustituciones
# Hamming -- sólo sustituciones por superposición. Una omisión da error para el resto de la cadena. DESCARTAR.
# LIPNS -- lo mismo, superposición.
# Smith-Waterman -- is more an alignment algorithm, used for DNA sequences

# Implement wagner-fischer? -- too old and inefficient, levenshtein is better
# Implement a weighted version of damerau-levenshtein? based on less penalty for:
#  - keyboard proximity (create a matrix of distance between keys? kbd language dependent!)
#  - additions of vowels? (as some transliterations may eat some vowels)

# Calculate similarity for DL-D based:
#  - edit distance weights less the longer the string is (the longer the str, the more feasible a typo is)
#  - use the length of the longer or the shorter str? make an average? some use longer norm = LD/max(len(a),len(b))
# ---> For the moment, the lib already has a normalised similarity interface. Check impl and decide if I do mine


# -- What about transposition of words? John Smith  vs Smith John  --> A proposal goes as this:
#  - Make a matrix of all the word pairs and calculate LD for all pairs (if different number, add empty strings)
#  - For each element in column, get minimum distance and remove that row and column (so, remove that row,
#    and the matched element in the remaining rows)
#  - resulting distance is the sum of all these minimums
# -> similar  to the Jaccard index, this should be normalised, so the resulting distance should be divided by
# the length of the string. either the number of words (smaller word would get the deal) or the total length
# in chars of words (the weight would be averaged), so maybe, we normalise each word-pair-distance and then
# we average?

# --> there is one small thing: result might differ if the leading string is one or the other. also if normalising
# per word (we should use the longest length of both paired words)

# -- Or if there is a full missing word? --> just ignore this condition. might be fatal if we attribute
# falsely a middle name --> on the above algorithm this goes right, as the distance would be maximal for missing words
# so they would be penalised

# maybe we can use a token alg to compare words [qval = None]: jaccard, dice or overlap  ---> do tests
#    with non-matching words, to see the rates there. Otherwise, we cna implement the above, which is more or less
#    the same but with fuzzy token matching.
# Jaccard is the number of common tokens (intersection) divided by the number of unique tokens in both
#   sets added (union minus intersection). it is vaguely similar to what's described above. There all terms are matched,
#   but with a LD weight
# Dice overestimates -- DISCARD
#


# Maybe in the end, do as nikos? use an average of LD and jaro-winkler? per token? encapsulate properly and then
# check with different options
