#!/usr/bin/python
# -*- coding: UTF-8 -*-

from engine import app


@app.route('/link/request/submit')
def bbb():
    return 'Hello World! 2'


@app.route('/link/<requestId>/status', methods=['POST'])
def ccc(requestId):
    return 'Hello World status! ' + requestId


