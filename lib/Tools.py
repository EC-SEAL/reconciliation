#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json

import yaml
from definitions import ROOT_DIR


def get_swagger_spec(spec_filepath):
    spec_path = os.path.join(ROOT_DIR, spec_filepath)
    with open(spec_path, 'r') as spec:
        return yaml.load(spec.read(), yaml.Loader)



   #  seal_yaml = get_swagger_spec("swagger/seal_ms_reconciliation.yaml")
   #


