#!/usr/bin/python
# -*- coding: UTF-8 -*-

# These tests will most probably fail for you, as they rely on a specific service being up and you
# having a RSA private key that is not on the repository.  # TODO: try to make them self-sustainable
import json
import unittest
import logging

from lib.CMHandler import CMHandler
from lib.SMHandler import SMHandler


class LinkTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(LinkTest, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True
        self.init_tests()

    def init_tests(self):
        pass

    def test_session_manager(self):
        cm = CMHandler('data/msMetadataList.json')
        sm = cm.get_microservice_by_api('SM')

        smh = SMHandler(sm, key='data/httpsig_key_esmo.pem', retries=5, validate=False)

        # Start session
        sessionID = smh.startSession()
        self.assertIsNotNone(sessionID)

        # Write variables
        sessval = 'testvalue' + sessionID
        dictval = {'dictvar': 'dictval'}
        smh.writeSessionVar(sessval, 'testvar')
        smh.writeSessionVar(dictval, 'testobj')

        # Read variables
        val = smh.getSessionVar('testvar')
        val2 = smh.getSessionVar('testobj')
        self.assertEqual(val, sessval)
        self.assertEqual(json.loads(val2), dictval)

        smh2 = SMHandler(sm, key='data/httpsig_key_esmo.pem', retries=5, validate=False)
        sesid2 = smh2.getSession('testvar', sessval)
        self.assertEqual(sessionID, sesid2)

        token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
        self.assertIsNotNone(token)

        smh3 = SMHandler(sm, key='data/httpsig_key_esmo.pem', retries=5, validate=False)
        add_data = smh3.validateToken(token)
        self.assertIsNone(add_data)
        self.assertEqual(sessionID, smh3.sessId)

        res = smh.endSession()
