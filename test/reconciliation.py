import unittest


# import pprint
# import logging

from lib.Tools import load_json_file
from lib.dto.Dto import cast_from_dict
from lib.dto.AttributeMap import AttributeMap
from lib.reconciliation import Reconciliation


class ReconciliationTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ReconciliationTests, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.INFO)
        self.init_tests()

    def init_tests(self):
        pass

    def test_set_matchings(self):
        arr = load_json_file('attributeMaps.json', encoding='utf8')
        r = Reconciliation()
        r.set_matchings(arr)
        self.assertIsNotNone(r.matchings)
        self.assertEqual(r.matchings[0].description, arr[0]['description'])

    def test_set_matchings_from_str(self):
        arr = load_json_file('attributeMaps.json', encoding='utf8')
        with open('attributeMaps.json', encoding='utf8') as json_file:
            json_str = json_file.read()
        r = Reconciliation()
        r.set_matchings_from_json(json_str)

        self.assertIsNotNone(r.matchings)
        self.assertEqual(r.matchings[0].description, arr[0]['description'])


if __name__ == '__main__':
    unittest.main()
