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

def get_send_html(status=None, kill_key=None):
    
    _status_lab = u'<span style="color:chartreuse">成功</span>' if status else u'<span style="color:red">失败</span>'
    _kill_lab = ''
    if int(kill_key) == 0:
        _kill_lab = u'<span style="color:chartreuse">已下发</span>'
    elif kill_key == 1:
        _kill_lab = u'<span style="color:red">已扣量</span>'
    elif kill_key == 2:
        _kill_lab = u'<span style="color:chocolate">省份屏蔽</span>'
    elif kill_key == 3:
        _kill_lab = u'<span style="color:blueviolet">黑名单</span>'
    elif kill_key == 4:
        _kill_lab = u'<span style="color:darkgreen">定制失败</span>'
    else:
        _kill_lab = ''
    return '%s|%s' % (_kill_lab, _status_lab)