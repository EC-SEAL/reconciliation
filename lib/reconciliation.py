#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Here make the main api of the reconciliation lib
import functools
import json

from config import config
from lib.comparison import Comparison
from lib.dto.AttributeMap import AttributeMap
from lib.dto.Dataset import Dataset
from lib.dto.Dto import cast_from_dict
from lib.processing import Processing

# Comparison Algorithm to use
comparison_alg = config.get('App', 'comparator', fallback="DamerauLevenshtein")

# Apply length-dependent weight to tuples
use_length_weight = config.getboolean('App', 'length_weight', fallback=False)


class Reconciliation:

    def __init__(self):
        self.processor = Processing()
        self.mappings = None
        self.comparator = Comparison()
        self.comparator.set_comparator(comparison_alg)

    def set_mappings(self, mappings: [dict]):
        self.mappings = []
        for mt in mappings:
            self.mappings.append(cast_from_dict(mt, AttributeMap))

    def set_mappings_from_json(self, mappings: str):
        self.set_mappings(json.loads(mappings))

    # Return a similarity level for two given datasets
    def similarity(self, dataset_a: Dataset, dataset_b: Dataset):

        if not isinstance(dataset_a, Dataset) \
                or not isinstance(dataset_b, Dataset):
            raise MissingOrBadParams("Passed parameters are not Dataset objects")

        # Build the tuple set to compare
        compare_tuples = self.processor.transform(dataset_a,
                                                  dataset_b,
                                                  self.mappings)
        if not len(compare_tuples):
            raise NoMatchingRules("No compare tuples could be generated")

        # Set the similarity of each tuple
        for ctuple in compare_tuples:
            ctuple.normalised_similarity = self.comparator.compare(ctuple.items[0],
                                                                   ctuple.items[1])

        # Calculate length dependent weight
        tuple_max_lengths = set()
        for ctuple in compare_tuples:
            # Get length of the maximum length string in tuple
            ctuple.max_length = len(max(ctuple.items, key=len))
            tuple_max_lengths.add(ctuple.max_length)

        # Maximum length of all tuples
        # tuples_max = max(tuple_max_lengths)

        # Sum of lengths of all tuples max
        sum_lengths = 0
        for ctuple in compare_tuples:
            sum_lengths = sum_lengths + ctuple.max_length

        # Calculate normalised weight
        for ctuple in compare_tuples:
            ctuple.length_weight = 1.0
            if use_length_weight:
                # ctuple.length_weight = ctuple.max_length / tuples_max
                ctuple.length_weight = ctuple.max_length / sum_lengths

        # Calculate normalised-weighted similarity for each tuple
        similarities = []
        for ctuple in compare_tuples:
            similarities.append(ctuple.normalised_similarity
                                * ctuple.weight
                                * ctuple.length_weight)

        # Calculate Dataset Similarity Coefficient (if not using length_weight,
        # because length_weight is already normalised)
        if use_length_weight:
            sim = functools.reduce(lambda a, b: a + b, similarities)
        else:
            sim = functools.reduce(lambda a, b: a + b, similarities) / len(similarities)

        return sim


class MissingOrBadParams(Exception):
    def __init__(self, message):
        self.message = message


class NoMatchingRules(Exception):
    def __init__(self, message):
        self.message = message

    # TODO: add accounting logs (INFO)
    # TODO: update swagger file with the final definitions and api
    # TODO: add json structure validation from the swagger definitions with bravado-core

    # Calculate similarity of the whole set of tuples
    # First, just consider the similarity, and normalise it. Later, decide how to weight
    # Considering all are equally important to the result, we need to add them, but the result is unbound
    # Max bound: each tuple has a max similarity of 1, so adding all of them and dividing by the count
    #   gives a max of 1.0 -> functools.reduce(lambda a,b: a+b, lst) / len(lst)
    # Now, if we don't want all elements to have the same importance, we need to reduce them.
    # We can have two types of weighting: individual or contextual:
    #  - Each item can be reduced proportionally (100% - 0%), so we multiply it by a value [0-1]
    #  - Each item can be reduced proportionally to each other
    # So, each tuple will have a 0-1 multiplication factor
    # And additionally, another optional factor: the weight of each tuple should depend on the max
    # length of the two compared strings in a tuple, relative to the rest of tuples. I mean: if
    # one compared tuple has twice the length of the rest, it should count twice. This would be meaningless
    # in, sets that include non-string data (numbers, dates), so deployer will activate it discretionally
    # So, calculate a second 0-1 multiplier:
    # - For each tuple i, calculate max len TMi
    # - For the TM list, calculate max TMm
    # - each mutiplier is: TMi / TMm
    # ctuple.weight
    # ctuple.normalised_similarity
    # weight as well the tuples based on the max length of the strings in the tuple
