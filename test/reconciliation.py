import unittest


# import pprint
# import logging


class ReconciliationTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ReconciliationTests, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.INFO)
        self.init_tests()

    def init_tests(self):
        pass

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
