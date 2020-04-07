#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import configparser

from definitions import PROPERTIES_FILE


def read_config(cfg_files):
    if cfg_files is None:
        return None

    if isinstance(cfg_files, str):
        cfg_files = [cfg_files]

    cfg = configparser.RawConfigParser()

    # merges all files into a single config
    for i, cfg_file in enumerate(cfg_files):
        if os.path.exists(cfg_file):
            cfg.read(cfg_file)

    return cfg


config_file_path = os.getenv('PROPERTIES_FILE', PROPERTIES_FILE)

if not os.path.exists(config_file_path):
    raise FileNotFoundError("Can't find properties file in path " + config_file_path)
if not os.path.isfile(config_file_path):
    raise FileExistsError("Given path for properties file is not a file: " + config_file_path)
if os.path.getsize(config_file_path) <= 0:
    raise FileExistsError("Properties file is empty: " + config_file_path)

config = read_config(config_file_path)
