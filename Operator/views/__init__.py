# coding=utf8
'''
Created on 2014-05-26
@author: brian
'''
import hashlib, hmac, re
import datetime
import time
from flask import jsonify, request, session, redirect, g
from sqlalchemy import or_, desc, func, and_
from sqlalchemy.orm import subqueryload

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


def get_mobile_is_block(mobile=None):
    if mobile:
        black_mb = g.session.query(PubBlackPhone).filter(PubBlackPhone.mobile==mobile).first()
        if black_mb:
            return True
    return False

def get_mobile_city_block(city=None, province=None, channel_id=None):
    _session = g.session #create_operator_session()
    if city and province:
        citys = _session.query(ChaProvince).\
                filter(ChaProvince.channelid==channel_id).\
                filter(ChaProvince.province==province).first()
        if citys:
            ct = "%s" % citys.city
            if ct:
                _index = ct.rfind("%s" % city)
                if _index>=0:
                  return False
                return True
            else:
                return True
    return True

def get_mobile_mr_count(mobile=None, channelid=None, is_day=False):
    _session = g.session
    if mobile and channelid:
        today = datetime.datetime.today()
        reg_date = "%s%s%s" % (today.year, today.month, today.day)
        if is_day:
            counts = _session.query(DataMr, func.count('mobile').label('count')).\
                            group_by(DataMr.regdate).\
                            filter(DataMr.mobile==mobile).\
                            filter(DataMr.channelid==channelid).\
                            filter(DataMr.regdate==reg_date).\
                            order_by(desc(DataMr.mobile)).all()
            if counts:
                return counts[0].count
            return 0
        else:
            #2014-10-%
            like_time = "%s-%s-%%" % (today.year, today.month)
            counts = _session.query(DataMr, func.count('mobile').label('count')).\
                                group_by(DataMr.regdate).\
                                filter(DataMr.mobile==mobile).\
                                filter(DataMr.channelid==channelid).\
                                filter(and_(DataMr.create_time.like(like_time))).\
                                order_by(desc(DataMr.mobile)).all()
            if counts:
                return counts[0].count
            return 0
def get_channel_province_count(usr_channel_id=None, cp_id=None, province=None):
    _session = g.session #create_operator_session()
    if usr_channel_id and cp_id:
        prov = _session.query(UsrProvince).filter(UsrProvince.channelid==usr_channel_id). filter(UsrProvince.cpid==cp_id).filter(UsrProvince.province == province).first()
        if prov:
            return prov.daymax
    return 0

def get_channel_count(channelid=None, cp_id=None, province=None, kill_data=-1):
    _session = create_operator_session()
    if channelid and cp_id:
        today = datetime.datetime.today()
        reg_date = "%s%s%s" % (today.year, today.month, today.day)
        counts = _session.query(DataMr, func.count('id').label('count')).\
                        filter(DataMr.channelid==channelid).\
                        filter(DataMr.regdate==reg_date).\
                        filter(DataMr.cpid == cp_id)

        if province:
            counts = counts.filter(DataMr.province==province)
        if kill_data >= 0:
            counts = counts.filter(DataMr.is_kill==kill_data)
        counts = counts.all()
        if counts:
            #print counts
            #print '======================='
            return counts[0].count
    return 0
