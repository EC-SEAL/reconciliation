#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

import json

from lib.preprocessor import Preprocessor
import pprint
import logging


class PreprocessorTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        # super(A, self).__init__(*args, **kwargs)
        super(PreprocessorTest, self).__init__(*args, **kwargs)
        logging.basicConfig(level=logging.INFO)
        # Setup logger
        self.init_tests()

    def init_tests(self):
        # Test data sets
        with open('testDatasets.json', encoding="utf8") as datasets_file:
            self.datasets = json.load(datasets_file)

        with open('attributeMaps.json', encoding="utf8") as matchings_file:
            self.matchings = json.load(matchings_file)

    def test_clean_string(self):
        input_string = "  legitimate-.,;:_·<>+\\|/'#@()\"\t\n\r!%&=?¡¿    text "
        expected_string = "legitimate text"
        p = Preprocessor()
        output_string = p.clean_string(input_string)
        output_string = p.clean_spaces(output_string)
        self.assertEqual(expected_string, output_string)

    def test_substitution(self):
        attributes = ["$CurrentGivenName", " ", "$FamilyName"]
        expected_str = "FRANCISCO JOSE ARAGO MONZONIS"
        p = Preprocessor()
        final_str = p.substitute(attributes, self.datasets[0])

        self.assertEqual(final_str, expected_str)


    def test_exact_match_after_transforms(self):
        p = Preprocessor()
        ctuples = p.transform(self.datasets[0],
                              self.datasets[1],
                              self.matchings)
        for tp in ctuples:
            self.assertEqual(tp[0], tp[1])

    def test_similar_match_after_transforms_greek(self):
         p = Preprocessor()
         ctuples = p.transform(self.datasets[2],
                               self.datasets[3],
                               self.matchings)
         self.assertEqual(ctuples[0][0], "ANDREAS PETROU")
         self.assertEqual(ctuples[0][1], "ANDREAS PETRO")

    # TODO: test cases:
    #  - for missing attributes in pairing
    #  - for an empty tuple item.
