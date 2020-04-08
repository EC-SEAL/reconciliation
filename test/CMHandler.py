import logging
import unittest

from lib.CMHandler import CMHandler


class CMHandlerTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CMHandlerTest, self).__init__(*args, **kwargs)
        logging.basicConfig(level=logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        self.init_tests()

    def init_tests(self):
        pass

    def testRemoteGet(self):
        # ms_url = "http://esmo.uji.es:8080/cm/metadata/microservices"
        ms_url = "http://lab9054.inv.uji.es/~paco/seal/msmetadata.json"
        cm = CMHandler('data/', key='data/httpsig_key_esmo.pem', lifetime=3, ms_source_url=ms_url)
        sm = cm.get_microservice_by_api('SM')

#  TODO: do mockup tests? or just have this as a sample test?
