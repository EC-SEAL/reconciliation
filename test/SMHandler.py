#!/usr/bin/python
# -*- coding: UTF-8 -*-

# These tests will most probably fail for you, as they rely on a specific service being up and you
# having a RSA private key that is not on the repository.  # TODO: try to make them self-sustainable
import json
import unittest
import logging

from lib.CMHandler import CMHandler
from lib.SMHandler import SMHandler, SessionManagerError
from lib.Tools import load_json_file
from lib.dto.StoreEntry import StoreEntry


class SMHandlerTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SMHandlerTest, self).__init__(*args, **kwargs)
        logging.basicConfig(level=logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        self.init_tests()

    def init_tests(self):
        pass

    def test_session_manager(self):
        cm = CMHandler('data/')
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

    def test_datastore_api(self):
        cm = CMHandler('data/')
        sm = cm.get_microservice_by_api('SM')

        smh = SMHandler(sm, key='data/httpsig_key_esmo.pem', retries=5, validate=False)

        lreq = load_json_file('data/testLinkRequest.json')
        storeEnt = StoreEntry()
        storeEnt.id = 'testID'
        storeEnt.type = 'linkRequest'
        storeEnt.data = lreq  # json.dumps(lreq)

        # Start session
        sessionID = smh.startSession()
        self.assertIsNotNone(sessionID)

        smh.resetDatastore()

        smh.addDatastoreEntry(storeEnt.id, storeEnt.type, storeEnt.data)

        read_req = smh.getDatastoreEntry(storeEnt.id)
        self.assertEqual(storeEnt.id, read_req.id)
        self.assertEqual(storeEnt.type, read_req.type)
        self.assertEqual(storeEnt.data['datasetA']['id'], read_req.data.datasetA.id)
        print("storeEnt.data:" + json.dumps(storeEnt.data))
        print("read_req.data:" + json.dumps(read_req.data.marshall()))

        read_reqs = smh.searchDatastoreEntries(storeEnt.type)
        read_req = read_reqs[0]
        self.assertEqual(storeEnt.id, read_req.id)
        self.assertEqual(storeEnt.type, read_req.type)
        self.assertEqual(storeEnt.data['datasetA']['id'], read_req.data.datasetA.id)

        smh.deleteDatastoreEntry(storeEnt.id)

        with self.assertRaises(SessionManagerError):
            smh.getDatastoreEntry(storeEnt.id)
