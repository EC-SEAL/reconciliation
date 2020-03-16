import unittest

from lib.Tools import load_json_file
from lib.dto.Dataset import Dataset
from lib.reconciliation import Reconciliation


class ReconciliationTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ReconciliationTests, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.INFO)
        self.init_tests()

    def init_tests(self):
        self.maps = load_json_file('data/attributeMaps.json', encoding='utf8')
        self.datasets = []
        datasets = load_json_file('data/testDatasets.json')
        for dt in datasets:
            d = Dataset()
            self.datasets.append(d.unmarshall(dt))

    def test_set_mappings(self):
        r = Reconciliation()
        r.set_mappings(self.maps)
        self.assertIsNotNone(r.mappings)
        self.assertEqual(r.mappings[0].description, self.maps[0]['description'])

    def test_set_mappings_from_str(self):
        with open('data/attributeMaps.json', encoding='utf8') as json_file:
            json_str = json_file.read()
        r = Reconciliation()
        r.set_mappings_from_json(json_str)
        self.assertIsNotNone(r.mappings)
        self.assertEqual(r.mappings[0].description, self.maps[0]['description'])

    def test_similarity_perfect(self):
        r = Reconciliation()
        r.set_mappings(self.maps)
        sim = r.similarity(self.datasets[0], self.datasets[1])
        self.assertEqual(sim, 1.0)

    def test_similarity_approximate(self):
        r = Reconciliation()
        r.set_mappings(self.maps)
        sim = r.similarity(self.datasets[2], self.datasets[3])
        self.assertGreaterEqual(sim, 0.9)


if __name__ == '__main__':
    unittest.main()
