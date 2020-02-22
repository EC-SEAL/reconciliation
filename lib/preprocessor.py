#!/usr/bin/python
# -*- coding: UTF-8 -*-


# Here implement the transformation of the input sets into a list of tuples of strings,
# using the input transformations


# Clean all - _ , . tabs, etc to separate words with just single spaces
import re
import string

from lib.transliteration import Transliteration


class Preprocessor:

    def __init__(self):
        self.trans = Transliteration()
        self.unwanted_chars = []
        pass

    # Input transfroms are only those relevant for the datasets being compared
    def transform(self, set_a, set_b, transforms):

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
                if 'regexp' in pr and pr['regexp'] is not None\
                        and 'replace' in pr and pr['replace'] is not None:
                    final_str = re.sub(pr['regexp'], pr['replace'], final_str)

                # Transliterate to ascii
                final_str = self.trans.to_ascii(final_str)

                #Clean useless chars:
                print("---")
                aaa="aaaa,. aaaa "
                print(aaa)
                # TODO: SEGUIR pasar un regexp replace y quitar los chars raros

                #string.whitespace
              #  final_str.safe_substitute()
              #  .translate(final_str,None,"\"'()-,.;/·+<>\\|"\t\n\r)
                # - split and joint, to remove multiple whitespaces .split()  aa=" ".join(str)

                compare_tuple.append(final_str)

            if len(compare_tuple) > 2:
                # TODO: log something, as this means the maps are not precise enough
                pass
            compare_tuples.append(compare_tuple)
        print(compare_tuples)
        return

    def substitute(self, attributeList, dataset):
        for item in attributeList:
            final_string = ""
            # It is a placeholder
            if item[0] == "$":
                # Seek it on the attrs at the dataset
                value = self.getAttributeValue(item[1:], dataset['attributes'])
                if value is not None:
                    final_string += value
            else:
                final_string += item
        return final_string

    def getAttributeValue(self, attr_name, attr_list):
        for attr in attr_list:
            if attr['name'] == attr_name or attr['friendlyName'] == attr_name:
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

    def build_string(self, dataset):
        return


class MapDatasetMatchNotFound(Exception):
    def __init__(self, message):
        self.message = message


# TODO: add a exhaustive logging in multiple levels to all of th module, to allow tracing and accounting

# TODO: weight each pair, so add the weoight to the outcome of the comparison
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
