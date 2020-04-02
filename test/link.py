#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unittest
import logging

from api.link import session_manager
from lib.CMHandler import CMHandler
from lib.SMHandler import SMHandler


class LinkTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(LinkTest, self).__init__(*args, **kwargs)
        logging.basicConfig(level=logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        self.init_tests()

    def init_tests(self):
        pass

    def test1(self):
        cm = CMHandler('data/msMetadataList.json')
        mss = cm.get_microservices()
        sm = cm.get_microservice_by_api('SM')

        smh = SMHandler(sm, key='data/httpsig_key_esmo.pem', retries=5, validate=False)
        print("------------------------------------------")
        smh.startSession()

        smh.writeSessionVar('testvalue', 'testvar')
        smh.writeSessionVar({'dictvar': 'dictval'}, 'testobj')


        val = smh.getSessionVar('testvar')
        val2 = smh.getSessionVar('testobj')

        print("testvar---->"+val)
        print("testobj---->"+val2)

        smh.endSession()

        #smh.generateToken('SAMLms_0001', 'ACMms001')
        #smh.getSessionVar("aaa")
