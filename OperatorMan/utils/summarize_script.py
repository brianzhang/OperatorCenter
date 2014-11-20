# coding=utf8
'''
Created on 2014-05-19
@author: brian
'''
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
import datetime
import calendar
import time
import hashlib, hmac, re
import string
import random
from functools import wraps
from sqlalchemy import or_, desc, func, distinct, CHAR, sql

from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync
from OperatorMan.configs import settings

def summarize_sp(regdate=None):
    session = create_operator_session()

    query_mdo = session.query(DataMr, func.count('price').label('total')).group_by(DataMr.regdate).group_by(DataMr.cpid).order_by(desc(DataMr.regdate))
    query_mdo = query_mdo.filter(DataMr.regdate==regdate).filter(DataMr.is_ivr==False)

    query_ivr = session.query(DataMr, func.sum(DataMr.momsg).label('total')).group_by(DataMr.regdate).group_by(DataMr.cpid).order_by(desc(DataMr.regdate))
    query_ivr = query_ivr.filter(DataMr.regdate==regdate).filter(DataMr.is_ivr==True)
    try:
        sp_operate_ivr_list = query_ivr.all()
        sp_operate_list = query_mdo.all()
        print '=========>',sp_operate_ivr_list
        if sp_operate_list or sp_operate_ivr_list:
            
            for item in sp_operate_list:
                count = float(item.total)
                item = item[0]
                account_sp = session.query(AccountSP).filter(AccountSP.js_date==regdate).\
                                filter(AccountSP.spid==item.channe_info.sp_info.id).filter(AccountSP.channelid==item.channe_info.id).first()
                if account_sp:
                    account_sp.count = count
                    account_sp.price = item.channe_info.price
                    account_sp.costprice = item.channe_info.costprice
                    account_sp.totalprice = count * account_sp.costprice
                    account_sp.create_time = datetime.datetime.now()
                else:
                    account_sp = AccountSP()
                    account_sp.spid = item.channe_info.sp_info.id
                    account_sp.channelid = item.channe_info.id
                    account_sp.count = count
                    account_sp.price = item.channe_info.price
                    account_sp.costprice = item.channe_info.costprice
                    account_sp.totalprice = count * account_sp.costprice
                    account_sp.js_state = False
                    account_sp.js_date = regdate
                    account_sp.create_time = datetime.datetime.now()

                session.add(account_sp)

            for item in sp_operate_ivr_list:
                print 'COUNT IVR SP: ', count
                count = float(item.total)
                item = item[0]
                account_sp = session.query(AccountSP).filter(AccountSP.js_date==regdate).\
                                filter(AccountSP.spid==item.channe_info.sp_info.id).filter(AccountSP.channelid==item.channe_info.id).first()
                if account_sp:
                    account_sp.count = count
                    account_sp.price = item.channe_info.price
                    account_sp.costprice = item.channe_info.costprice
                    account_sp.totalprice = count * account_sp.costprice
                    account_sp.create_time = datetime.datetime.now()
                else:
                    account_sp = AccountSP()
                    account_sp.spid = item.channe_info.sp_info.id
                    account_sp.channelid = item.channe_info.id
                    account_sp.count = count
                    account_sp.price = item.channe_info.price
                    account_sp.costprice = item.channe_info.costprice
                    account_sp.totalprice = count * account_sp.costprice
                    account_sp.js_state = False
                    account_sp.js_date = regdate
                    account_sp.create_time = datetime.datetime.now()

                session.add(account_sp)

            session.commit()
            session.close()
            print 'summarize SP ok.'
    except Exception, e:
        print 'ERROR SPP:', e
        session.close()

def summarize_cp(regdate=None):
    session = create_operator_session()
    today = datetime.datetime.today()

    query = session.query(DataMr, func.count('price').label('total')).filter(DataMr.is_kill==0).\
            group_by(DataMr.regdate).group_by(DataMr.cpid).order_by(desc(DataMr.regdate))
    query = query.filter(DataMr.regdate==regdate)

    query_ivr = session.query(DataMr, func.sum(DataMr.momsg).label('total')).filter(DataMr.is_kill==0).\
                group_by(DataMr.regdate).group_by(DataMr.cpid).order_by(desc(DataMr.regdate))

    query_ivr = query_ivr.filter(DataMr.regdate==regdate).filter(DataMr.is_ivr==True)

    try:
        sp_operate_ivr_list = query_ivr.all()
        sp_operate_list = query.all()
        if sp_operate_list or sp_operate_ivr_list:
            
            for item in sp_operate_list:
                count = float(item.total)
                item = item[0]
                account_cp = session.query(AccountCP).filter(AccountCP.js_date==regdate).\
                                filter(AccountCP.cpid==item.cpid).filter(AccountCP.channelid==item.channelid).first()
                if account_cp:
                    account_cp.count = count
                    account_cp.price = item.channe_info.price
                    account_cp.fcprice = item.channe_info.fcpric
                    account_cp.totalprice = count * account_cp.fcprice
                    account_cp.create_time = datetime.datetime.now()
                else:
                    account_cp = AccountCP()
                    account_cp.cpid = item.cpid
                    account_cp.channelid = item.channelid
                    account_cp.count = count
                    account_cp.price = item.channe_info.price
                    account_cp.fcprice = item.channe_info.fcpric
                    account_cp.totalprice = float(count) * account_cp.fcprice
                    account_cp.js_state = False
                    account_cp.js_date = regdate
                    account_cp.create_time = datetime.datetime.now()

                session.add(account_cp)

            for item in sp_operate_ivr_list:
                count = float(item.total)
                print 'COUNT IVR: ', count

                item = item[0]
                account_cp = session.query(AccountCP).filter(AccountCP.js_date==regdate).\
                                filter(AccountCP.cpid==item.cpid).filter(AccountCP.channelid==item.channelid).first()
                if account_cp:
                    account_cp.count = count
                    account_cp.price = item.channe_info.price
                    account_cp.fcprice = item.channe_info.fcpric
                    account_cp.totalprice = float(count) * account_cp.fcprice
                    account_cp.create_time = datetime.datetime.now()
                else:
                    account_cp = AccountCP()
                    account_cp.cpid = item.cpid
                    account_cp.channelid = item.channelid
                    account_cp.count = count
                    account_cp.price = item.channe_info.price
                    account_cp.fcprice = item.channe_info.fcpric
                    account_cp.totalprice = float(count) * account_cp.fcprice
                    account_cp.js_state = False
                    account_cp.js_date = regdate
                    account_cp.create_time = datetime.datetime.now()

                session.add(account_cp)

            session.commit()
            session.close()
            print 'summarize CP ok.'
    except Exception, e:
        print 'ERROR:', e
        session.close()

if __name__ == '__main__':
    print '=======start========'
    print sys.argv
    regdate = None
    if len(sys.argv) >= 2:
        regdate = sys.argv[1]
    else:
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s%s%s" % (today.year, _month, _day)

    print 'summarize data:', regdate
    summarize_sp(regdate)
    summarize_cp(regdate)
    print '=======end========='