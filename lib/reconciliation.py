#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Here make the main api of the reconciliation lib
# - receive string pairing info and transform the input sets (call)
# - transliterate each pair of strings (loop, 2 calls)
# - compare the strings (loop, 1 call)
# - return awarded level of similarity for the input sets

from lib.preprocessor import Preprocessor

class Reconciliation:

    def __init__(self):
        self.preprocessor = Preprocessor()
        pass






    '''
    
            with open('testDatasets.json', encoding="utf8") as datasets_file:
            self.datasets = json.load(datasets_file)

        with open('attributeMaps.json', encoding="utf8") as matchings_file:
            self.matchings = json.load(matchings_file)

    
        ctuples = p.transform(self.datasets[2],
                              self.datasets[3],
                              self.matchings)
    
    
    '''


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
