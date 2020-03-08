#!/usr/bin/python
# -*- coding: UTF-8 -*-


# Here implement the transformation of the input sets into a list of tuples of strings,
# using the input transformations


# Clean all - _ , . tabs, etc to separate words with just single spaces
import re
import string
import logging

from lib.transliteration import Transliteration


class Preprocessor:

    def __init__(self):
        self.trans = Transliteration()
        self.unwanted_chars = "-.,;:_·<>+\\\|/'#@()\"\t\n\r!%&=?¡¿"
        pass

    # Input transfroms are only those relevant for the datasets being compared
    def transform(self, set_a, set_b, transforms):
        logging.debug("preprocessor.transform")
        logging.debug("Transforms: "+str(transforms))
        logging.debug("Dataset A: "+str(set_a))
        logging.debug("Dataset B: "+str(set_b))
        # Loop the maps, and feed from the datasets.
        # Each map will produce a tuple to be compared
        compare_tuples = []
        for tr in transforms:

            compare_tuple = []
            for pr in tr['pairings']:
                # Get dataset of a type, issuer and categories
                try:
                    st = self.match_set(pr['profile'],
                                        pr['issuer'],
                                        pr['categories'],
                                        set_a, set_b)
                except MapDatasetMatchNotFound:
                    # If pairing does not match this case, we fail silently and go on
                    continue

                # Substitute placeholders for attributes and Concatenate.
                # (if attr not found, fail silently and leave empty string)
                final_str = self.substitute(pr['attributes'], st)

                # Match and replace if required
                if 'regexp' in pr and pr['regexp'] is not None \
                        and 'replace' in pr and pr['replace'] is not None:
                    final_str = re.sub(pr['regexp'], pr['replace'], final_str)

                # Transliterate to ascii
                final_str = self.trans.to_ascii(final_str)

                # Clean useless chars and trim spaces:
                final_str = self.clean_string(final_str)
                final_str = self.clean_spaces(final_str)

                # Uppercase the string
                final_str = final_str.upper()

                # Add the resulting string to the tuple
                compare_tuple.append(final_str)

            # If something weird happened, sanitize, log warning and go on
            if len(compare_tuple) > 2:
                # TODO: log something, as this means the maps are not precise enough
                compare_tuple = (compare_tuple[0], compare_tuple[1])

            # Avoid two-empty string comparisons
            if compare_tuple[0] != "" or compare_tuple[1] != "":
                compare_tuples.append(compare_tuple)
            else:
                # TODO: log something, as this means the maps are not precise enough
                pass

        return compare_tuples

    def substitute(self, attribute_list, dataset):
        logging.debug("preprocessor.substitute")
        logging.debug("attribute_list: "+str(attribute_list))
        logging.debug("dataset: "+str(dataset))

        if not attribute_list:
            # TODO decide how to behave if no attributes were passed, for the moment, just empty string
            return ""

        final_string = ""
        for item in attribute_list:
            logging.debug("item: "+item)

            # It is a placeholder
            if item[0] == "$":
                logging.debug("It is a placeholder")
                # Seek it on the attrs at the dataset
                value = self.getAttributeValue(item[1:], dataset['attributes'])
                if value is not None:
                    logging.debug("Returned value: " + value)
                    final_string = final_string + value
                    logging.debug("final_string: " + final_string)
                else:
                    logging.warning("attribute "+item[1:]+" not found in dataset: "+ str(dataset['attributes']))
            else:
                final_string = final_string + item
                logging.debug("final_string: " + final_string)
        logging.debug("returning final_string: " + final_string)
        return final_string

    def getAttributeValue(self, attr_name, attr_list):
        logging.debug("preprocessor.getAttributeValue")
        logging.debug("attr_name:"+attr_name)
        logging.debug("attr_list:"+str(attr_list))
        for attr in attr_list:
            name = set([attr['name'], attr['friendlyName']])
            if attr_name in name:
                logging.debug("found")
                return attr['values'][0]
        return None

    # Will return which of the datasets matches the criteria, or launch an exception otherwise
    def match_set(self, profile, issuer, categories, set_a, set_b):
        sets = [set_a, set_b]
        found = False
        for st in sets:
            # If type does not match, skip
            if st['type'] != profile:
                continue
            # If there is a fixed issuer
            if issuer is not None:
                if st['issuerId'] is None or st['issuerId'] == "":
                    continue
                if st['issuerId'] not in st['attributes']:
                    continue
                if st['attributes'][st['issuerId']] != profile:
                    continue
            found = True
            # If there are fixed categories to find (one found is ok)
            if categories is not None and categories != []:
                found = False
                for cat in categories:
                    if cat in st['categories']:
                        found = True
                        break
            if found:
                return st
        if not found:
            raise MapDatasetMatchNotFound("Passed datasets do not fulfill the criteria")

    def clean_string(self, input_string):
        return re.sub("[" + self.unwanted_chars + "]", ' ', input_string)

    def clean_spaces(self, input_string):
        s = re.sub("\s+", ' ', input_string)
        return s.strip()


class MapDatasetMatchNotFound(Exception):
    def __init__(self, message):
        self.message = message


# TODO: add a exhaustive logging in multiple levels to all of th module, to allow tracing and accounting

# TODO: weight each pair, so add the weight to the outcome of the comparison
# To select the list of transforms:
# From all the maps, get only those that are relevant fro this case:
#    - get a map if both dataset types are the profile of at least two of the pairings
#    - if issuer is defined, get a map just if both dataset issuers are on the pairings
#    - if categories are defined in the data sets, get a map just if categories of both datasets
#      are on the categories of some pairings (each dataset on a pairing, of course)

'''
def json_validator(data):
    try:
        json.loads(data)
        return True
    except ValueError as error:
        print("invalid json: %s" % error)
        return False
'''
