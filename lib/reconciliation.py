#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Here make the main api of the reconciliation lib



import json

from config import config
from lib.comparison import Comparison
from lib.dto.AttributeMap import AttributeMap
from lib.dto.Dataset import Dataset
from lib.dto.Dto import cast_from_dict
from lib.processing import Processing


# Comparison Algorithm to use
comparison_alg = config.get('App', 'comparator', fallback="DamerauLevenshtein")


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
        # Set the similarity of each tuple
        for ctuple in compare_tuples:
            ctuple.normalised_similarity = self.comparator.compare(ctuple.items[0],
                                                                   ctuple.items[1])

        # Calculate similarity of the whole set of tuples
        # ctuple.weight
        # ctuple.normalised_similarity
        # weight as well the tuples based on the max length of the strings in the tuple


    # TODO: SEGUIR:



class MissingOrBadParams(Exception):
    def __init__(self, message):
        self.message = message



# TODO: add accounting logs (INFO)
# TODO: update swagger file with the final definitions and api
# TODO: add json structure validation from the swagger definitions with bravado-core
