#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unittest
import logging

from lib.Tools import load_json_file
from lib.dto.LinkRequest import LinkRequest
from lib.reconciliation import Reconciliation, NoMatchingRules


class LinkTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(LinkTest, self).__init__(*args, **kwargs)
        self.init_tests()

    def init_tests(self):
        pass

    def test_1(self):
        maps = load_json_file('data/attributeMaps.json', encoding='utf8')
        reqj = load_json_file('data/testLinkRequest.json', encoding='utf8')

        lreq = LinkRequest()
        lreq.unmarshall(reqj)

        r = Reconciliation()
        r.set_mappings(maps)
        sim = r.similarity(lreq.datasetA, lreq.datasetB)
        print(reqj)
        print(sim)
        self.assertEqual(sim, 1.0)

    def test_2(self):
        maps = load_json_file('data/attributeMaps.json', encoding='utf8')
        reqj = load_json_file('data/testLinkRequest2.json', encoding='utf8')

        lreq = LinkRequest()
        lreq.unmarshall(reqj)

        r = Reconciliation()
        r.set_mappings(maps)
        sim = r.similarity(lreq.datasetA, lreq.datasetB)
        print(reqj)
        print(sim)
        self.assertEqual(sim, 1.0)

    def test_3(self):
        maps = load_json_file('data/attributeMaps.json', encoding='utf8')
        reqj = load_json_file('data/testLinkRequest3.json', encoding='utf8')

        lreq = LinkRequest()
        lreq.unmarshall(reqj)

        r = Reconciliation()
        r.set_mappings(maps)
        sim = r.similarity(lreq.datasetA, lreq.datasetB)
        print(reqj)
        print(sim)
        self.assertEqual(sim, 1.0)

    def test_4(self):
        maps = load_json_file('data/attributeMaps.json', encoding='utf8')
        reqj = load_json_file('data/testLinkRequest4.json', encoding='utf8')

        lreq = LinkRequest()
        lreq.unmarshall(reqj)

        r = Reconciliation()
        r.set_mappings(maps)
        with self.assertRaises(NoMatchingRules) as context:
            sim = r.similarity(lreq.datasetA, lreq.datasetB)
