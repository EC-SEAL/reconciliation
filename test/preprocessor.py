#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from lib.Tools import load_json_file
from lib.dto.AttributeMap import AttributeMap
from lib.dto.Dataset import Dataset
from lib.preprocessor import Preprocessor, MapDatasetMatchNotFound


class PreprocessorTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PreprocessorTest, self).__init__(*args, **kwargs)
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
        p = Preprocessor()
        output_string = p.clean_spaces(input_string)
        self.assertEqual(expected_string, output_string)

    def test_clean_string(self):
        input_string = "  legitimate-.,;:_·<>+\\|/'#@()\"\t\n\r!%&=?¡¿    text "
        expected_string = "legitimate text"
        p = Preprocessor()
        output_string = p.clean_string(input_string)
        output_string = p.clean_spaces(output_string)
        self.assertEqual(expected_string, output_string)

    def test_no_match_set(self):
        profile = "fail"
        issuer = "fail"
        categories = ["None", "to", "be", "found"]
        p = Preprocessor()
        with self.assertRaises(MapDatasetMatchNotFound):
            p.match_set(profile, issuer, categories,
                        self.datasets[0],
                        self.datasets[1])

    def test_no_getAttributeValue(self):
        attr_name = "fail"
        attr_list = self.datasets[0].attributes
        p = Preprocessor()
        value = p.getAttributeValue(attr_name, attr_list)
        self.assertIsNone(value)

    def test_substitution(self):
        attributes = ["$CurrentGivenName", " ", "$FamilyName"]
        expected_str = "FRANCISCO JOSE ARAGO MONZONIS"
        p = Preprocessor()
        final_str = p.substitute(attributes, self.datasets[0])

        self.assertEqual(final_str, expected_str)

    def test_substitution_no_attrs(self):
        attributes = []
        p = Preprocessor()
        final_str = p.substitute(attributes, self.datasets[0])

        self.assertEqual(final_str, "")

    def test_substitution_notfound(self):
        attributes = ["$NotToBeFound", "ZZ", "$FamilyName"]
        expected_str = "ZZARAGO MONZONIS"
        p = Preprocessor()
        final_str = p.substitute(attributes, self.datasets[0])

        self.assertEqual(final_str, expected_str)

    def test_transform_exact_match(self):
        p = Preprocessor()
        ctuples = p.transform(self.datasets[0],
                              self.datasets[1],
                              self.mappings)

        self.assertGreaterEqual(len(ctuples), 1)
        for tp in ctuples:
            self.assertEqual(tp[0], tp[1])

    def test_transform_similar_match_greek(self):
        p = Preprocessor()
        ctuples = p.transform(self.datasets[2],
                              self.datasets[3],
                              self.mappings)

        self.assertEqual(len(ctuples), 1)
        self.assertEqual(ctuples[0][0], "ANDREAS PETROU")
        self.assertEqual(ctuples[0][1], "ANDREAS PETRO")


if __name__ == '__main__':
    unittest.main()
