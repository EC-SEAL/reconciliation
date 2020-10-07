#!/usr/bin/python
# -*- coding: UTF-8 -*-
import base64
import hashlib
import os
import json
import re
import time
from urllib.parse import quote

from requests import Request

import yaml

from definitions import ROOT_DIR
from lib.dto.Dataset import Dataset


def load_json_file(file_path, encoding='utf8'):
    with open(file_path, encoding=encoding) as json_file:
        return json.load(json_file)


def clean_string(input_string, unwanted_chars=" "):
    return re.sub("[" + unwanted_chars + "]", ' ', input_string)


def clean_spaces(input_string):
    s = re.sub("\\s+", ' ', input_string)
    return s.strip()


def sha256_fingerprint(key_pem):
    key_pem = re.sub('[-]+BEGIN PUBLIC KEY[-]+', '', key_pem)
    key_pem = re.sub('[-]+END PUBLIC KEY[-]+', '', key_pem)
    key_pem = key_pem.strip()
    key_pem = key_pem.replace("\n\r", '')
    key_pem = key_pem.replace("\n", '')
    key_pem = key_pem.replace("\r", '')

    key_bin = base64.b64decode(key_pem)
    return hashlib.sha256(key_bin).hexdigest()


def gmt_time():
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())


def pretty_print_http(req: Request):
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------BEGIN REQUEST-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


def get_swagger_spec(spec_filepath):
    spec_path = os.path.join(ROOT_DIR, spec_filepath)
    with open(spec_path, 'r') as spec:
        return yaml.load(spec.read(), yaml.Loader)


#  seal_yaml = get_swagger_spec("swagger/seal_ms_reconciliation.yaml")
#


def build_store_id_from_req(module, issuer, datasetA, datasetB):
    subjectA = indirect_search(datasetA.subjectId, datasetA)
    issuerA = indirect_search(datasetA.issuerId, datasetA)
    subjectB = indirect_search(datasetB.subjectId, datasetB)
    issuerB = indirect_search(datasetB.issuerId, datasetB)
    return build_store_id(module, issuer, subjectA, issuerA, subjectB, issuerB)


def build_store_id(module, linkIssuer, subjectA, issuerA, subjectB, issuerB):
    if not module:
        raise Exception("No module name provided")
    if not linkIssuer:
        raise Exception("No link issuer name provided")
    if not subjectA:
        raise Exception("No subject A id provided")
    if not issuerA:
        raise Exception("No issuer A id provided")
    if not subjectB:
        raise Exception("No subject B id provided")
    if not issuerB:
        raise Exception("No issuer B id provided")

    module_id = quote(module)
    linkIssuer_id = quote(linkIssuer)

    identityA = f"{quote(subjectA)}:{quote(issuerA)}"
    identityB = f"{quote(subjectB)}:{quote(issuerB)}"

    # Id must be commutative for the two implied identities, we set them in alphabetic order
    if identityA <= identityB:
        firstIdentity = identityA
        secondIdentity = identityB
    else:
        firstIdentity = identityB
        secondIdentity = identityA

    return f"urn:mace:project-seal.eu:id:{module_id}:{linkIssuer_id}:{firstIdentity}:{secondIdentity}"


# Search the first value of a given attribute in the dataSet
def indirect_search(key, dataSet):
    for attr in dataSet.attributes:
        if key in {attr.friendlyName, attr.name}:
            return attr.values[0]
    return None


def build_uri_representation_from_req(LinkIssuerId, LLoA, datasetA, datasetB):
    subjectA = indirect_search(datasetA.subjectId, datasetA)
    issuerA = indirect_search(datasetA.issuerId, datasetA)
    subjectB = indirect_search(datasetB.subjectId, datasetB)
    issuerB = indirect_search(datasetB.issuerId, datasetB)
    return build_uri_representation(LinkIssuerId, LLoA, subjectA, issuerA, subjectB, issuerB)


def build_uri_representation(LinkIssuerId, LLoA, subjectA, issuerA, subjectB, issuerB):
    if not LLoA:
        raise Exception("No LLoA provided")
    if not LinkIssuerId:
        raise Exception("No link issuer ID provided")
    if not subjectA:
        raise Exception("No subject A id provided")
    if not issuerA:
        raise Exception("No issuer A id provided")
    if not subjectB:
        raise Exception("No subject B id provided")
    if not issuerB:
        raise Exception("No issuer B id provided")

    LinkIssuerId = quote(LinkIssuerId)
    LLoA = quote(LLoA)

    identityA = f"{quote(subjectA)}:{quote(issuerA)}"
    identityB = f"{quote(subjectB)}:{quote(issuerB)}"

    # Id must be commutative for the two implied identities, we set them in alphabetic order
    if identityA <= identityB:
        firstIdentity = identityA
        secondIdentity = identityB
    else:
        firstIdentity = identityB
        secondIdentity = identityA

    return f"urn:mace:project-seal.eu:link:{LinkIssuerId}:{LLoA}:{subjectA}:{issuerA}:{subjectB}:{issuerB}"
