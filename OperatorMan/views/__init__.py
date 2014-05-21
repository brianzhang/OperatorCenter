# coding=utf8
'''
Created on 2014-05-19
@author: brian
'''
import hashlib, hmac, re
from flask import jsonify, request, session, redirect
from functools import wraps
from OperatorMan.configs import settings

def _jsonify(status, code='', data={}):
    return jsonify(ok=status, reason=code, data=data)
    
def ok_json(code='', data={}):
    return _jsonify(True, code, data)
    
def fail_json(code='', data={}):
    return _jsonify(False, code, data)

def hash_password(password):
    m = hmac.new(settings.SECRET_KEY, password, hashlib.sha1)
    return m.hexdigest()