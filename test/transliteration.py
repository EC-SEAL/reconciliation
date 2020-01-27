#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from lib.transliteration import Transliteration


class TransliterationTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        # super(A, self).__init__(*args, **kwargs)
        super(TransliterationTest, self).__init__(*args, **kwargs)

        self.init_tests()

    def init_tests(self):
        # Test Strings
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

    def test_case_ascii_ascii(self):
        res = self.trans.to_ascii(self.strings['latin_l1'])
        self.assertEqual(res, self.strings['latin_l1'])

    def test_case_latin_ascii(self):
        res = self.trans.to_ascii(self.strings['iso_latin_test'])
        self.assertEqual(res, self.strings['iso_latin_expected'])

    def test_case_greek_ascii_multichar(self):
        res = self.trans.to_ascii(self.strings['th_greek_test'])
        self.assertEqual(res, self.strings['th_greek_expected'])

    def test_case_ascii_greek(self):
        res = self.trans.to_alphabet(self.strings['latin_l1'], target_language='el')
        self.assertEqual(res, self.strings['greek_el'])

    def test_case_greek_ascii(self):
        res = self.trans.to_ascii(self.strings['greek_el'])
        self.assertEqual(res, self.strings['latin_l1'])

    def test_case_russian_ascii(self):
        res = self.trans.to_ascii(self.strings['russian_ru'])
        self.assertEqual(res, self.strings['latin_l1'])

    # def test_case_ukrainian_ascii(self):
    #     res = self.trans.to_ascii(self.strings['ukrainian_uk'])
    #     self.assertEqual(res, self.strings['latin_l1'])

    def test_case_serbian_ascii(self):
        res = self.trans.to_ascii(self.strings['serbian_sr'])
        self.assertEqual(res, self.strings['latin_l1'])

    def test_case_bulgarian_ascii(self):
        res = self.trans.to_ascii(self.strings['bulgarian_bg'])
        self.assertEqual(res, self.strings['latin_l1'])

    def test_case_macedonian_ascii(self):
        res = self.trans.to_ascii(self.strings['macedonian_mk'])
        self.assertEqual(res, self.strings['latin_l1'])

    # def test_case_mongolian_ascii(self):
    #     res = self.trans.to_ascii(self.strings['mongolian_mn'])
    #     self.assertEqual(res, self.strings['latin_l1'])

    # def test_case_georgian_ascii(self):
    #     res = self.trans.to_ascii(self.strings['georgian_ka'])
    #     self.assertEqual(res, self.strings['latin_l1'])

    def test_case_armenian_ascii(self):
        res = self.trans.to_ascii(self.strings['armenian_hy'])
        self.assertEqual(res, self.strings['latin_l1'])
