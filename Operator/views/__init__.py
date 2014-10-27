# coding=utf8
'''
Created on 2014-05-26
@author: brian
'''
import hashlib, hmac, re
from flask import jsonify, request, session, redirect, g
from Operator.configs import settings

from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync


def _jsonify(status, code='', data={}):
    return jsonify(ok=status, reason=code, data=data)

def ok_json(code='', data={}):
    return _jsonify(True, code, data)

def fail_json(code='', data={}):
    return _jsonify(False, code, data)

def hash_password(password):
    m = hmac.new(settings.SECRET_KEY, password, hashlib.sha1)
    return m.hexdigest()

def querySPInfo(sp_id=None):
    if sp_id:
        sp_info = g.session.query(UsrSPInfo).filter(UsrSPInfo.id==sp_id).first()
        if sp_info:
            return sp_info
        else:
            return None
    else:
        return None

def get_mobile_attribution(mobile=None):
    if mobile:
        mobile = mobile[0:7]
        mobile_info = g.session.query(PubMobileArea).filter(PubMobileArea.mobile == mobile).all()

        if mobile_info:
            return mobile_info[0]
    return None
