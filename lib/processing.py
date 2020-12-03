#!/usr/bin/python
# -*- coding: UTF-8 -*-


# Here implement the transformation of the input sets into a list of tuples of strings,
# using the input transformations. The resulting tuples will be compared and based on their similarity, a
# To select the list of transforms:
# From all the maps, get only those that are relevant fro this case:
#    - get a map if both dataset types are the profile of at least two of the pairings
#    - if issuer is defined, get a map just if both dataset issuers are on the pairings
#    - if categories are defined in the data sets, get a map just if categories of both datasets
#      are on the categories of some pairings (each dataset on a pairing, of course)


import re
import logging
from typing import List

from lib.processors.base.Processors import Processors
from lib.dto.Dataset import Dataset, Attribute
from lib.dto.AttributeMap import AttributeMap
from lib.dto.CompareTuple import CompareTuple
from lib.processors.base.processor import Processor


class Processing:

    def __init__(self):
        self.processors = Processors()
        pass

    # Input transformations are only those relevant for the datasets being compared
    def transform(self, set_a: Dataset, set_b: Dataset, transforms: List[AttributeMap]):
        logging.debug("preprocessor.transform")
        logging.debug("Transforms: " + str(transforms))
        logging.debug("Dataset A: " + str(set_a))
        logging.debug("Dataset B: " + str(set_b))
        # Loop the maps, and feed from the datasets.
        # Each map will produce a tuple to be compared
        compare_tuples = []
        for transform in transforms:

            # If no processor is defined, we default to string
            proc_type = transform.processor
            if proc_type not in self.processors.list():
                proc_type = "str"
            processor = self.processors.get(proc_type)

            # Check if both datasets (of a type, issuer and categories)
            # have at least one matching rule on the map
            pairings_a = self.match_set(set_a, transform)
            pairings_b = self.match_set(set_b, transform)
            if len(pairings_a) == 0 or len(pairings_b) == 0:
                continue

            # Process each set with one of the matching pairings to generate a compare string candidate
            tuple_candidates_a = set()
            tuple_candidates_b = set()
            for pair in pairings_a:
                compare_string = self.process(set_a, pair, processor)
                if compare_string:
                    tuple_candidates_a.add(compare_string)
            for pair in pairings_b:
                compare_string = self.process(set_b, pair, processor)
                if compare_string:
                    tuple_candidates_b.add(compare_string)

            # For some weird reason, no strings were produced, so
            # ignore and go on with the next transform
            if not len(tuple_candidates_a) or not len(tuple_candidates_b):
                logging.warning("A transform with valid pairings returned an empty string for the tuple")
                continue

            # As potentially multiple compare strings may have generated from equivalent
            # rules, choose the one that will provide a stronger match
            tuple_member_a = self.best_candidate(tuple_candidates_a, processor)
            tuple_member_b = self.best_candidate(tuple_candidates_b, processor)

            # Build the tuple
            compare_tuple = CompareTuple()
            compare_tuple.weight = transform.weight
            compare_tuple.items.append(tuple_member_a)
            compare_tuple.items.append(tuple_member_b)

            # Add it to the compare set
            compare_tuples.append(compare_tuple)

        return compare_tuples

    # Return a string consisting of the concatenation of the array items, previously substituting
    # variables for the attribute values in the data set
    def substitute(self, attribute_list: List[str], dataset: Dataset):
        logging.debug("preprocessor.substitute")
        logging.debug("attribute_list: " + str(attribute_list))
        logging.debug("dataset: " + str(dataset))

        if not attribute_list:
            logging.warning("No attributes were passed. Returning empty string")
            return ""

        final_string = ""
        for item in attribute_list:
            logging.debug("item: " + item)

            # It is a placeholder
            if item[0] == "$":
                logging.debug("It is a placeholder")
                # Seek it on the attrs at the dataset
                value = self.getAttributeValue(item[1:], dataset.attributes)
                if value is not None:
                    logging.debug("Returned value: " + value)
                    final_string = final_string + value
                    logging.debug("final_string: " + final_string)
                else:
                    logging.warning("attribute " + item[1:] + " not found in dataset: " + str(dataset.attributes))
            else:
                final_string = final_string + item
                logging.debug("final_string: " + final_string)
        logging.debug("returning final_string: " + final_string)
        return final_string

    def getAttributeValue(self, attr_name, attr_list: List[Attribute]):
        logging.debug("preprocessor.getAttributeValue")
        logging.debug("attr_name:" + attr_name)
        logging.debug("attr_list:" + str(attr_list))
        for attr in attr_list:
            name = {attr.name, attr.friendlyName}
            if attr_name in name:
                logging.debug("found")
                return attr.values[0]
        return None

    # For all the pairings in a map, will return those that fit the dataset
    def match_set(self, dataset: Dataset(), attr_map: AttributeMap()):

        # Get the issuer of the data set
        set_issuer = None
        if dataset.issuerId is not None and dataset.issuerId != '':
            iss = None
            for attr in dataset.attributes:
                if attr.name == dataset.issuerId:
                    iss = attr.values[0]
                    break
            if iss is not None and iss != '':
                set_issuer = iss

        # Check all pairings to see if they are valid for this dataset
        valid_pairings = set()
        for pair in attr_map.pairings:

            # If there is a fixed issuer in the pairing, check it
            if pair.issuer is not None and set_issuer is not None:
                if pair.issuer == set_issuer:
                    valid_pairings.add(pair)
                continue

            # If there's type and does not match, skip
            if dataset.type is not None and pair.profile is not None:
                if dataset.type == pair.profile:
                    valid_pairings.add(pair)
                continue

            # If there are fixed categories to find (one found is ok)
            if pair.categories is not None and pair.categories != []:
                for cat in pair.categories:
                    if cat in dataset.categories:
                        valid_pairings.add(pair)
                        break

        return valid_pairings

    # Generate a compare string from an attribute set and a pairing rule
    def process(self, attr_set, pair, processor):

        # Substitute placeholders for attributes and Concatenate.
        # (if attr not found, fail silently and leave empty string)
        final_str = self.substitute(pair.attributes, attr_set)

        # Match and replace if required
        if pair.regexp is not None \
                and pair.replace is not None:
            final_str = re.sub(pair.regexp, pair.replace, final_str)

        # Process input data according to data type
        final_str = processor.process(final_str)

        return final_str

    def best_candidate(self, tuple_candidates, processor: Processor()):
        best = None
        for candidate in tuple_candidates:
            if best is None:
                # First item, automatic best
                best = candidate
                continue
            # Compare with last
            best = processor.best(best, candidate)

        if best is None:
            raise NoTupleCandidates("The candidates set for a compare string in a tuple is empty")

        return best


class MapDatasetMatchNotFound(Exception):
    def __init__(self, message):
        self.message = message


class NoTupleCandidates(Exception):
    def __init__(self, message):
        self.message = message
