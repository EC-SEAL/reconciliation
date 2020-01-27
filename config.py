#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import configparser


def read_config(cfg_files):
    if cfg_files is None:
        return None

    if isinstance(cfg_files, str):
        cfg_files = [cfg_files]

    config = configparser.RawConfigParser()

    # merges all files into a single config
    for i, cfg_file in enumerate(cfg_files):
        if os.path.exists(cfg_file):
            config.read(cfg_file)

    return config


config = read_config("server.properties")
