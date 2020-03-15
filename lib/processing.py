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

            compare_tuple = CompareTuple()
            compare_tuple.weight = transform.weight
            for pair in transform.pairings:
                # Get dataset of a type, issuer and categories
                try:
                    st = self.match_set(pair.profile,
                                        pair.issuer,
                                        pair.categories,
                                        set_a, set_b)
                except MapDatasetMatchNotFound:
                    # If pairing does not match this case, we fail silently and go on
                    continue

                # Substitute placeholders for attributes and Concatenate.
                # (if attr not found, fail silently and leave empty string)
                final_str = self.substitute(pair.attributes, st)

                # Match and replace if required
                if pair.regexp is not None \
                        and pair.replace is not None:
                    final_str = re.sub(pair.regexp, pair.replace, final_str)

                # If no processor is defined, we default to string
                proc_type = transform.processor
                if proc_type not in self.processors.list():
                    proc_type = "str"
                processor = self.processors.get(proc_type)

                # Process input data according to data type
                final_str = processor.process(final_str)

                # Add the resulting object to the tuple
                compare_tuple.items.append(final_str)

            # If something weird happened, sanitize, log warning and go on
            if len(compare_tuple.items) > 2:
                logging.warning("A tuple had more than 2 elements. Maps are not precise enough")
                print(compare_tuple)
                compare_tuple.items = [compare_tuple.items[0], compare_tuple.items[1]]

            # Avoid two-empty string comparisons
            if compare_tuple.items[0] != "" or compare_tuple.items[1] != "":
                compare_tuples.append(compare_tuple)
            else:
                logging.warning("Both elements in a tuple were empty strings. Maps are not precise enough")

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

    # Will return which of the datasets matches the criteria, or launch an exception otherwise
    def match_set(self, profile, issuer, categories, set_a, set_b):
        sets = [set_a, set_b]
        found = False
        for st in sets:
            # If type does not match, skip
            if st.type != profile:
                continue
            # If there is a fixed issuer
            if issuer is not None:
                if st.issuerId is None or st.issuerId == "":
                    continue
                if st.issuerId not in st.attributes:
                    continue
                if st.attributes[st.issuerId] != profile:
                    continue
            found = True
            # If there are fixed categories to find (one found is ok)
            if categories is not None and categories != []:
                found = False
                for cat in categories:
                    if cat in st.categories:
                        found = True
                        break
            if found:
                return st
        if not found:
            raise MapDatasetMatchNotFound("Passed datasets do not fulfill the criteria")


class MapDatasetMatchNotFound(Exception):
    def __init__(self, message):
        self.message = message
