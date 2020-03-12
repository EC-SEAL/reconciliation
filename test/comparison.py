#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from lib.comparison import Comparison


class ComparisonTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ComparisonTest, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.DEBUG)
        self.init_tests()

    def init_tests(self):
        pass

    def test_case_match_match(self):
        a = "TestString"
        b = "TestString"

        comp = Comparison()
        comp.set_comparator("CaseSensitiveMatch")
        res = comp.compare(a, b)

        self.assertEqual(res, 1)

    def test_case_match_fail(self):
        a = "TestString"
        b = "TestString1"

        comp = Comparison()
        comp.set_comparator("CaseSensitiveMatch")
        res = comp.compare(a, b)

        self.assertEqual(res, 0)

    def test_caseless_match_match(self):
        a = "TestString"
        b = "testString"

        comp = Comparison()
        comp.set_comparator("CaseInsensitiveMatch")
        res = comp.compare(a, b)

        self.assertEqual(res, 1)

    def test_caseless_match_fail(self):
        a = "TestString"
        b = "testString1"

        comp = Comparison()
        comp.set_comparator("CaseInsensitiveMatch")
        res = comp.compare(a, b)

        self.assertEqual(res, 0)

    def test_levenshtein_match_success(self):
        a = "aaaa"
        b = "aaaa1"
        threshold = 0.7

        comp = Comparison()
        comp.set_comparator("LevenshteinDistance")
        res = comp.compare(a, b)

        self.assertGreaterEqual(res, threshold)

    def test_damerau_match_success(self):
        a = "aaaa"
        b = "aaaa1"
        threshold = 0.7

        comp = Comparison()
        comp.set_comparator("DamerauLevenshtein")
        res = comp.compare(a, b)

        self.assertGreaterEqual(res, threshold)

    def test_damerau_match_perfect(self):
        a = "aaaa"
        b = "aaaa"
        threshold = 1

        comp = Comparison()
        comp.set_comparator("DamerauLevenshtein")
        res = comp.compare(a, b)

        self.assertEqual(res, threshold)

    def test_damerau_match_fail(self):
        a = "aabc"
        b = "aaaa"
        threshold = 0.7

        comp = Comparison()
        comp.set_comparator("DamerauLevenshtein")
        res = comp.compare(a, b)

        self.assertLess(res, threshold)

    def test_damerau_match_zero(self):
        a = "frbc"
        b = "aaaa"
        threshold = 0

        comp = Comparison()
        comp.set_comparator("DamerauLevenshtein")
        res = comp.compare(a, b)

        self.assertEqual(res, threshold)


if __name__ == '__main__':
    unittest.main()
