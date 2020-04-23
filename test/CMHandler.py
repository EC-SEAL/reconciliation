import logging
import unittest

from lib.CMHandler import CMHandler

# Before running these tests, you need urls to point to a properly functioning
# Config Manager microservice. Either substitute here the domain in the urls
# or set configManager to be resolved in your /etc/hosts file to the proper domain

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
        ms_url = "http://configManager:8080/cm/metadata/microservices"
        cm = CMHandler('data/', key='data/httpsig_key_esmo.pem', lifetime=3, ms_source_url=ms_url)
        sm = cm.get_microservice_by_api('SM')

#  TODO: do mockup tests? or just have this as a sample test?
