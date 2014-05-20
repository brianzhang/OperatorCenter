# coding=utf8
'''
Created on 2014-05-19
@author: brian
'''

from flask import jsonify, request, session, redirect
from functools import wraps
from OperatorMan.configs import settings

def _jsonify(status, code='', data={}):
    return jsonify(ok=status, reason=code, data=data)
    
def ok_json(code='', data={}):
    return _jsonify(True, code, data)
    
def fail_json(code='', data={}):
    return _jsonify(False, code, data)


def check_login(leave=True, redir=None):
    '''
    @param leave: 是否直接跳出本路由
    @param redir: 要跳转的路径，当leave=True时，该参数才生效，如果没指定该值，则默认返回json信息，否则跳转到指定页面
    '''
    def run(func):
        @wraps(func)
        def wrapper(*args, **kv):
            if '_sid' in session:
                session_id = session['_sid']
                req = rest.Request(settings.P_QUERY_SESSION_URI)
                req.token = session_id
                resp = req.fetch()
                if resp.ok:
                    request._session_id = session_id
                    request._is_auth = True
                    request._user = resp.data
                    return func(*args, **kv)
            if leave:
                if redir:
                    return redirect(redir)
                # return fail_json(error.NO_TOKEN.ls
                	code, u'登陆超时')
                return u'登陆超时'
            else:
                request._user = None
                request._is_auth = False
                return func(*args, **kv)
        return wrapper
    return run


def check_administrator(func):
    @wraps(func)
    def wrapper(*args, **kv):
        if request._user['user_type'] == 'administrator':
            return func(*args, **kv)
        # return fail_json(error.WARN_PERMISSION.code, error.WARN_PERMISSION.desc)
        return u'没有权限'
    return wrapper

def check_app_admin(func):
    @wraps(func)
    def wrapper(*args, **kv):
        if request._user['user_type'] == 'app_admin':
            return func(*args, **kv)
        # return fail_json(error.WARN_PERMISSION.code, error.WARN_PERMISSION.desc)
        return u'没有权限'
    return wrapper

def check_app_manager(func):
    @wraps(func)
    def wrapper(*args, **kv):
        user_type = request._user['user_type']
        if user_type == 'app_admin' or user_type == 'app_manager':
            return func(*args, **kv)
        # return fail_json(error.WARN_PERMISSION.code, error.WARN_PERMISSION.desc)
        return u'没有权限'
    return wrapper