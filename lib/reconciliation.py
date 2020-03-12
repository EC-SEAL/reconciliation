#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Here make the main api of the reconciliation lib
# - receive string pairing info and transform the input sets (call)
# - transliterate each pair of strings (loop, 2 calls)
# - compare the strings (loop, 1 call)
# - return awarded level of similarity for the input sets


import json

from config import config
from lib.comparison import Comparison
from lib.dto.AttributeMap import AttributeMap
from lib.dto.Dataset import Dataset
from lib.dto.Dto import cast_from_dict
from lib.preprocessor import Preprocessor


# Comparison Algorithm to use
comparison_alg = config.get('App', 'comparator', fallback="DamerauLevenshtein")


class Reconciliation:

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.matchings = None
        self.comparator = Comparison()
        self.comparator.set_comparator(comparison_alg)


    def set_matchings(self, matchings: [dict]):
        self.matchings = []
        for mt in matchings:
            self.matchings.append(cast_from_dict(mt, AttributeMap))

    def set_matchings_from_json(self, matchings: str):
        self.set_matchings(json.loads(matchings))

    # Return a similarity level for two given datasets
    def similarity(self, dataset_a: Dataset, dataset_b: Dataset):

        if not isinstance(dataset_a, Dataset) \
                or not isinstance(dataset_b, Dataset):
            raise MissingOrBadParams("Passed parameters are not Dataset objects")

        # Build the tuple set to compare
        compare_tuples = self.preprocessor.transform(dataset_a,
                                                     dataset_b,
                                                     self.matchings)

        for ctuple in compare_tuples:
            pass



class MissingOrBadParams(Exception):
    def __init__(self, message):
        self.message = message



# TODO: add accounting logs (INFO)
# TODO: update swagger file with the final definitions and api
# TODO: weight each pair, so add the weight to the outcome of the comparison
# TODO: maybe, besides the tuple weight, add an additional weight based on the length of the compared strings?
# TODO: add json structure validation from the swagger definitions with bravado-core
# TODO: if possible, move dictionaries to classes (it is huge work, as from py 3.0, you can't set the internal
#  dictionary of the object and the named tuples method doesn't allow to update the fields) --> created a base class to solve this:
# TODO SEGUIR: modelar dtos a usar, cambiar código actual por los DTOs, run tests, crear dto para las tuplas y añadir el weight

'''

        a = "aabc"
        b = "aaaa"
        threshold = 0.7

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.damerau_levenshtein)
        res = comp.compare(a, b)


       self.strings = {
            'latin_l1': "Lorem ipsum dolor sit amet",

            'greek_el': "Λορεμ ιψυμ δολορ σιτ αμετ",
            'russian_ru': "Лорем ипсум долор сит амет",
            'ukrainian_uk': "Лорем іпсум долор сіт амет",
            'serbian_sr': "Лорем ипсум долор сит амет",
            'bulgarian_bg': "Лорем ипсум долор сит амет",
            'macedonian_mk': "Лорем ипсум долор сит амет",
            'mongolian_mn': "Лорэм ипсүм долор сит амэт",
            'georgian_ka': "ლორემ იპსუმ დოლორ სით ამეთ",
            'armenian_hy': "Լօրեմ իպսում դօլօր սիտ ամետ",

            'th_greek_test': "Θεμις",
            'th_greek_expected': "Themis",
            'iso_latin_test': "áçñéíóúàèìòùâêÎÔûßðþø",
            'iso_latin_expected': "atsneiouaeiouaeIOussdthoe",
        }

       self.trans = Transliteration()

        res = self.trans.to_ascii(self.strings['latin_l1'])
        self.assertEqual(res, self.strings['latin_l1'])

        res = self.trans.to_ascii(self.strings['iso_latin_test'])
        self.assertEqual(res, self.strings['iso_latin_expected'])

        res = self.trans.to_ascii(self.strings['th_greek_test'])
        self.assertEqual(res, self.strings['th_greek_expected'])

'''
