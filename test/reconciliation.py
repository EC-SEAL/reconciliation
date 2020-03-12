import unittest

from lib.Tools import load_json_file
from lib.reconciliation import Reconciliation


class ReconciliationTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ReconciliationTests, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.INFO)
        self.init_tests()

    def init_tests(self):
        pass

    def test_set_mappings(self):
        arr = load_json_file('data/attributeMaps.json', encoding='utf8')
        r = Reconciliation()
        r.set_mappings(arr)
        self.assertIsNotNone(r.mappings)
        self.assertEqual(r.mappings[0].description, arr[0]['description'])

    def test_set_mappings_from_str(self):
        arr = load_json_file('data/attributeMaps.json', encoding='utf8')
        with open('data/attributeMaps.json', encoding='utf8') as json_file:
            json_str = json_file.read()
        r = Reconciliation()
        r.set_mappings_from_json(json_str)

        self.assertIsNotNone(r.mappings)
        self.assertEqual(r.mappings[0].description, arr[0]['description'])


if __name__ == '__main__':
    unittest.main()
