#!/usr/bin/python
# -*- coding: UTF-8 -*-


import unittest

import lib.comparison


class ComparisonTest(unittest.TestCase):

    def test_case_match_match(self):
        a = "TestString"
        b = "TestString"

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.case_match)
        res = comp.compare(a, b)

        self.assertEqual(res, 1)

    def test_case_match_fail(self):
        a = "TestString"
        b = "TestString1"

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.case_match)
        res = comp.compare(a, b)

        self.assertEqual(res, 0)

    def test_caseless_match_match(self):
        a = "TestString"
        b = "testString"

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.caseless_match)
        res = comp.compare(a, b)

        self.assertEqual(res, 1)

    def test_caseless_match_fail(self):
        a = "TestString"
        b = "testString1"

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.caseless_match)
        res = comp.compare(a, b)

        self.assertEqual(res, 0)

    def test_damerau_match_success(self):
        a = "aaaa"
        b = "aaaa1"
        threshold = 0.7

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.damerau_levenshtein)
        res = comp.compare(a, b)

        self.assertGreaterEqual(res, threshold)

    def test_damerau_match_perfect(self):
        a = "aaaa"
        b = "aaaa"
        threshold = 1

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.damerau_levenshtein)
        res = comp.compare(a, b)

        self.assertEqual(res, threshold)

    def test_damerau_match_fail(self):
        a = "aabc"
        b = "aaaa"
        threshold = 0.7

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.damerau_levenshtein)
        res = comp.compare(a, b)

        self.assertLess(res, threshold)


    def test_damerau_match_zero(self):
        a = "frbc"
        b = "aaaa"
        threshold = 0

        comp = lib.comparison.Comparators()
        comp.set_comparator(lib.comparison.damerau_levenshtein)
        res = comp.compare(a, b)

        self.assertEqual(res, threshold)


if __name__ == '__main__':
    unittest.main()
