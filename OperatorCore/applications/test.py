
import datetime
import time
import urllib2, urllib
import simplejson as json
import os
import sys
import md5
import hashlib, hmac, re

reload(sys)
sys.setdefaultencoding("utf-8")

from sqlalchemy import or_, desc, func
from sqlalchemy.orm import subqueryload

from datetime import timedelta

from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync, create_operator_session, SysRights


session = create_operator_session()

def hash_password(password):
    m = hmac.new('96e2b3699a852ade9d4d2fd408c93612', password, hashlib.sha1)
    return m.hexdigest()

def add_SysRole():

    sysRole = SysRole()
    sysRole.rolename = 'sysAdmin'
    sysRole.is_show = True
    sysRole.content = "all"
    sysRole.rights = 'all'

    try:
        session.add(sysRole)
        session.commit()

    except Exception, e:
        print 'error in SysRole:'
        print e

def add_user():
    print '========add test user...====='
    sysAdmin = SysAdmin()
    sysAdmin.username = 'brian'
    sysAdmin.userpwd = hash_password('123')
    sysAdmin.realname = 'brian'
    sysAdmin.role_id = 1
    sysAdmin.phone = '15815515601'
    sysAdmin.qq = '372114189'
    sysAdmin.email = 'brian.netmad@gmail.com'
    sysAdmin.is_show = True
    sysAdmin.content = 'test user'
    sysAdmin.create_time = datetime.datetime.now()

    try:
        session.add(sysAdmin)
        session.commit()
    except Exception, e:
        print 'Error in SysAdmin'
        print e

def add_sysRights():
    print '=======add test SysRights========='
    sysRights = SysRights()
    sysRights.rightname = "channel Manage"
    sysRights.is_show = True
    sysRights.create_time = datetime.datetime.now()
    try:
        session.add(sysRights)
        session.commit()
    except Exception, e:
        print 'Error in SysRights'
        print e

if __name__ == '__main__':

    #add_SysRole()
    add_sysRights()
    add_user()
