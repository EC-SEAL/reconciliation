#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import unittest

import loader
from definitions import COMP_DIR


class ComparisonTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ComparisonTest, self).__init__(*args, **kwargs)
        logging.basicConfig(level=logging.DEBUG)
        self.init_tests()

    def init_tests(self):
        pass

    def test_aaa(self):

        mods = loader.load_classes(COMP_DIR, globals())
        print(mods)

        aa = damerauLevenshtein.damerauLevenshtein()
        print("---", aa.compare("abc", "acb"))  # TODO: SEGUIR.

        modname = "damerauLevenshtein"
        classname = "damerauLevenshtein"
        module = globals()[modname]
        class_ = getattr(module, classname)
        inst = class_()
        print("---", inst.compare("abc", "acb"))  # TODO: SEGUIR.


        # lib.comparison.load_comparators()
        # print(comparators.__all__)
        # for mod in comparators.__all__:
        #     print("MOD: ", mod)
        #     module = importlib.import_module(mod)
        #     print(module)
        #     class_ = getattr(module, mod)
        #     inst = class_()
        #     #inst = levenshtein.levenshtein()
        #     print("---",inst.compare("a","a"))  # TODO: sEGUIR.
        #
        # bb = Comparators()
        #
        # print(bb.list_comparators())

    # def test_case_match_match(self):
    #     a = "TestString"
    #     b = "TestString"
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.case_match)
    #     res = comp.compare(a, b)
    #
    #     self.assertEqual(res, 1)
    #
    # def test_case_match_fail(self):
    #     a = "TestString"
    #     b = "TestString1"
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.case_match)
    #     res = comp.compare(a, b)
    #
    #     self.assertEqual(res, 0)
    #
    # def test_caseless_match_match(self):
    #     a = "TestString"
    #     b = "testString"
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.caseless_match)
    #     res = comp.compare(a, b)
    #
    #     self.assertEqual(res, 1)
    #
    # def test_caseless_match_fail(self):
    #     a = "TestString"
    #     b = "testString1"
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.caseless_match)
    #     res = comp.compare(a, b)
    #
    #     self.assertEqual(res, 0)
    #
    # def test_damerau_match_success(self):
    #     a = "aaaa"
    #     b = "aaaa1"
    #     threshold = 0.7
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.damerau_levenshtein)
    #     res = comp.compare(a, b)
    #
    #     self.assertGreaterEqual(res, threshold)
    #
    # def test_damerau_match_perfect(self):
    #     a = "aaaa"
    #     b = "aaaa"
    #     threshold = 1
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.damerau_levenshtein)
    #     res = comp.compare(a, b)
    #
    #     self.assertEqual(res, threshold)
    #
    # def test_damerau_match_fail(self):
    #     a = "aabc"
    #     b = "aaaa"
    #     threshold = 0.7
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.damerau_levenshtein)
    #     res = comp.compare(a, b)
    #
    #     self.assertLess(res, threshold)
    #
    #
    # def test_damerau_match_zero(self):
    #     a = "frbc"
    #     b = "aaaa"
    #     threshold = 0
    #
    #     comp = lib.comparison.Comparators()
    #     comp.set_comparator(lib.comparison.damerau_levenshtein)
    #     res = comp.compare(a, b)
    #
    #     self.assertEqual(res, threshold)


if __name__ == '__main__':
    unittest.main()
