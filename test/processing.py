#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from lib import Tools
from lib.Tools import load_json_file
from lib.dto.AttributeMap import AttributeMap
from lib.dto.Dataset import Dataset
from lib.processing import Processing, MapDatasetMatchNotFound
from lib.processors.StringProcessor import StringProcessor
from lib.processors.base.Processors import Processors


class ProcessorTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ProcessorTest, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.DEBUG)
        self.init_tests()

    def init_tests(self):
        # Test data sets
        self.datasets = []
        datasets = load_json_file('data/testDatasets.json')
        for dt in datasets:
            d = Dataset()
            self.datasets.append(d.unmarshall(dt))

        self.mappings = []
        mappings = load_json_file('data/attributeMaps.json')
        for mt in mappings:
            m = AttributeMap()
            self.mappings.append(m.unmarshall(mt))

    def test_clean_spaces(self):
        input_string = "   a  b    c    d "
        expected_string = "a b c d"
        p = Processing()
        output_string = Tools.clean_spaces(input_string)
        self.assertEqual(expected_string, output_string)

    def test_clean_string(self):
        input_string = "  legitimate-.,;:_·<>+\\|/'#@()\"\t\n\r!%&=?¡¿    text "
        expected_string = "legitimate text"
        p = Processing()
        output_string = Tools.clean_string(input_string, StringProcessor.unwanted_chars)
        output_string = Tools.clean_spaces(output_string)
        self.assertEqual(expected_string, output_string)

    def test_no_match_set(self):
        profile = "fail"
        issuer = "fail"
        categories = ["None", "to", "be", "found"]
        p = Processing()
        with self.assertRaises(MapDatasetMatchNotFound):
            p.match_set(profile, issuer, categories,
                        self.datasets[0],
                        self.datasets[1])

    def test_no_getAttributeValue(self):
        attr_name = "fail"
        attr_list = self.datasets[0].attributes
        p = Processing()
        value = p.getAttributeValue(attr_name, attr_list)
        self.assertIsNone(value)

    def test_substitution(self):
        attributes = ["$CurrentGivenName", " ", "$FamilyName"]
        expected_str = "FRANCISCO JOSE ARAGO MONZONIS"
        p = Processing()
        final_str = p.substitute(attributes, self.datasets[0])

        self.assertEqual(final_str, expected_str)

    def test_substitution_no_attrs(self):
        attributes = []
        p = Processing()
        final_str = p.substitute(attributes, self.datasets[0])

        self.assertEqual(final_str, "")

    def test_substitution_notfound(self):
        attributes = ["$NotToBeFound", "ZZ", "$FamilyName"]
        expected_str = "ZZARAGO MONZONIS"
        p = Processing()
        final_str = p.substitute(attributes, self.datasets[0])

        self.assertEqual(final_str, expected_str)

    def test_transform_exact_match(self):
        p = Processing()
        ctuples = p.transform(self.datasets[0],
                              self.datasets[1],
                              self.mappings)

        self.assertGreaterEqual(len(ctuples), 1)
        for tp in ctuples:
            self.assertEqual(tp.items[0], tp.items[1])

    def test_transform_similar_match_greek(self):
        p = Processing()
        ctuples = p.transform(self.datasets[2],
                              self.datasets[3],
                              self.mappings)

        self.assertEqual(len(ctuples), 1)
        self.assertEqual(ctuples[0].items[0], "ANDREAS PETROU")
        self.assertEqual(ctuples[0].items[1], "ANDREAS PETRO")

    def test_transform_date_ok(self):
        expected_str = "1956-03-24"
        input_str = "24/03/1956"
        processors = Processors()
        processor = processors.get("DateProcessor")
        final_str = processor.process(input_str)
        self.assertEqual(final_str, expected_str)

    def test_transform_date_fail(self):
        input_str = "this is not a date"
        expected_str = "this is not a date"
        processors = Processors()
        processor = processors.get("DateProcessor")
        final_str = processor.process(input_str)
        self.assertEqual(final_str, expected_str)

    def test_transform_number_ok(self):
        expected_str = "1432578.0"
        input_str = "  1432578aaa   "
        processors = Processors()
        processor = processors.get("NumberProcessor")
        final_str = processor.process(input_str)
        self.assertEqual(final_str, expected_str)

    def test_transform_number_fail(self):
        input_str = "this is not a number"
        expected_str = "this is not a number"
        processors = Processors()
        processor = processors.get("NumberProcessor")
        final_str = processor.process(input_str)
        self.assertEqual(final_str, expected_str)


if __name__ == '__main__':
    unittest.main()
