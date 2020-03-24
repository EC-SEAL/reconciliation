#!/usr/bin/python
# -*- coding: UTF-8 -*-
import base64
import hashlib
import os
import json
import re
import time
from requests import Request


import yaml

from definitions import ROOT_DIR


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
