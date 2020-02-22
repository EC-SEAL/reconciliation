#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

import json

from lib.preprocessor import Preprocessor
import pprint


class PreprocessorTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        # super(A, self).__init__(*args, **kwargs)
        super(PreprocessorTest, self).__init__(*args, **kwargs)

        self.init_tests()

    def init_tests(self):
        # Test data sets
        with open('testDatasets.json') as datasets_file:
            self.datasets = json.load(datasets_file)

        with open('attributeMaps.json') as matchings_file:
            self.matchings = json.load(matchings_file)

        # pp = pprint.PrettyPrinter(indent=4)
        # print("TEST DATA SETS")
        # print("--------------")
        # pp.pprint(self.datasets)
        # print("TEST MATCHINGS")
        # print("--------------")
        # pp.pprint(self.matchings)

    def test_case_1(self):

        p = Preprocessor()
        p.transform(self.datasets[0],
                    self.datasets[1],
                    self.matchings)
        self.assertEqual(1, 1)
