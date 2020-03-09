#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Here make the main api of the reconciliation lib
# - receive string pairing info and transform the input sets (call)
# - transliterate each pair of strings (loop, 2 calls)
# - compare the strings (loop, 1 call)
# - return awarded level of similarity for the input sets


class Reconciliation:

    def __init__(self):
        pass


# TODO: add accounting logs (INFO)
# TODO: update swagger file
# TODO: weight each pair, so add the weight to the outcome of the comparison
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
