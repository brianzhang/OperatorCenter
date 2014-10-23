# coding=utf8
'''
Created on 2014-05-19
@author: brian
'''
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import datetime
import time
import hashlib, hmac, re
import string
import random
from flask import jsonify, request, session, redirect, g
from functools import wraps
from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, create_operator_session
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

def random_key(size=6, chars=string.ascii_uppercase + string.digits):
    size = 6
    return ''.join(random.choice(chars) for _ in range(size))

def write_sys_log(_type, _title, _content, _uid):
    get_session = create_operator_session()
    sys_log = SysAdminLog()
    sys_log.adminid = _uid
    sys_log.op_type = _type
    sys_log.op_title = _title
    sys_log.op_content = _content
    sys_log.create_time = datetime.datetime.now()

    try:
        get_session.add(sys_log)
        get_session.commit()
        return True
    except Exception, e:
        get_session.rollback()
        return False
