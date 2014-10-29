# -*- coding: utf-8 -*-

import datetime
import time
import urllib2, urllib
import simplejson
import os
import sys
import md5
import random

reload(sys)
sys.setdefaultencoding("utf-8")

from sqlalchemy import or_, desc, func
from sqlalchemy.orm import subqueryload
from datetime import timedelta
from flask import request, render_template, jsonify, g, Blueprint, Response, redirect, session, url_for

from werkzeug import secure_filename
from Operator.configs import settings
from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync


from Operator.views import querySPInfo, get_mobile_attribution, \
                get_mobile_is_block, get_mobile_mr_count, \
                get_channel_province_count, get_channel_count

operator_view = Blueprint('operator_view', __name__)

@operator_view.route('/MO/<int:SP_ID>/<channel_id>/', methods=["GET"])
def channel_mo(channel_id=None, SP_ID=None):
    req = request.args if request.method == 'GET' else request.form
    sp_info = True#querySPInfo(SP_ID)
    if channel_id and SP_ID:
        channel_info = g.session.query(UsrSPSync).filter(UsrSPSync.channelid==channel_id).filter(UsrSPSync.spid==SP_ID).first()
        if channel_info:

            spnumber = req.get(channel_info.spnumber, None)
            mobile = req.get(channel_info.mobile, None)
            linkid = req.get(channel_info.linkid, None)
            msg = req.get(channel_info.msg, None)

            if channel_info.status_name:                
                status_name = req.get(channel_info.status_name, '')
                status_val = channel_info.status_val

            if channel_info.type_name:
                type_name = req.get(channel_info.type_name, '')
                type_key = channel_info.spnumber

            mobile_info = get_mobile_attribution(mobile)

            data_mo = g.session.query(DataMo).filter(DataMo.channelid == channel_id).filter(DataMo.linkid==linkid).first()
            
            if data_mo:
                return "False"
            else:
                data_mo = DataMo()

            data_mo.mobile = mobile
            data_mo.momsg = msg

            cp_list = g.session.query(UsrChannel).filter(UsrChannel.channelid== channel_id).filter(UsrChannel.is_show == True).all()
            if cp_list:
                cp = random.sample(cp_list, 1)
                data_mo.cpid = cp[0].cpid

            data_mo.channelid = channel_id
            data_mo.spnumber = spnumber
            data_mo.price = channel_info.cha_info.price
            data_mo.linkid = linkid
            data_mo.province = mobile_info.province
            data_mo.city = mobile_info.city
            today = datetime.datetime.today()
            data_mo.regdate = "%s%s%s" % (today.year, today.month, today.day)
            data_mo.reghour = today.hour
            data_mo.create_time = datetime.datetime.now()

            ever_day = g.session.query(DataEverday).filter(DataEverday.channelid==channel_id).\
                            filter(DataEverday.cpid==data_mo.cpid).\
                            filter(DataEverday.province==data_mo.province).\
                            filter(DataEverday.city == data_mo.city).\
                            filter(DataEverday.tj_hour==data_mo.reghour).one()

            if ever_day:
                ever_day.mo_all += 1
                ever_day.datetime = datetime.datetime.now()
            else:
                ever_day = DataEverday()
                ever_day.channelid = channel_id
                ever_day.cpid = data_mo.cpid
                ever_day.price = data_mo.price
                ever_day.province = data_mo.province
                ever_day.city = data_mo.city
                ever_day.tj_hour = data_mo.reghour
                ever_day.mo_all = 1
                ever_day.mr_all = 0
                ever_day.mr_cp = 0
                ever_day.tj_date = data_mo.regdate
                ever_day.create_time = datetime.datetime.now()

            try:
                g.session.add(data_mo)
                g.session.add(ever_day)
                g.session.commit()                    
                return "OK"
            except Exception, e:
                return "False"
            # query mobile attribution
            # query channel sync count
            #  计算是否扣量
            # INSERT OR UPDATE DATA_MO
            # if not  is_kill
            # sync CP data.

        return "False"

    return jsonify({'ok': False, 'SP_ID': SP_ID, 'MSG': 'The SP IS UNDEFINED'})

@operator_view.route('/MR/<int:SP_ID>/<channel_id>/', methods=["GET"])
def channel_mr(channel_id=None,SP_ID=None):
    req = request.args if request.method == 'GET' else request.form
    sp_info = True#querySPInfo(SP_ID)
    if channel_id and SP_ID:
        
        channel_info = g.session.query(UsrSPSync).filter(UsrSPSync.channelid==channel_id).filter(UsrSPSync.spid==SP_ID).first()
        if channel_info:

            spnumber = req.get(channel_info.spnumber, None)
            mobile = req.get(channel_info.mobile, None)
            linkid = req.get(channel_info.linkid, None)
            msg = req.get(channel_info.msg, None)

            if channel_info.status_name:                
                status_name = req.get(channel_info.status_name, '')
                status_val = channel_info.status_val

            if channel_info.type_name:
                type_name = req.get(channel_info.type_name, '')
                type_key = channel_info.spnumber

            if not mobile:
                mobile_mo = g.session.query(DataMo).filter(DataMo.linkid==linkid).filter(DataMo.channelid==channel_id).first()
                if mobile_mo:
                    mobile = mobile_mo.mobile            
            
            #UsrProvince
            data_mr = g.session.query(DataMr).filter(DataMr.channelid == channel_id).filter(DataMr.linkid==linkid).first()
            if  data_mr:
                return "False"
            else:
                data_mr = DataMr()

            data_mr.mobile = mobile
            data_mr.momsg = msg
            mobile_info = get_mobile_attribution(mobile) # query mobile area
            is_kill = False
            is_block = get_mobile_is_block(mobile) # query mobile is block
            day_count = get_mobile_mr_count(mobile, channel_id, True) #query mobile day count
            month_count = get_mobile_mr_count(mobile, channel_id, False) #query mobile month count
            channel_day_max = channel_info.cha_info.daymax # query channel day max
            channel_month_max = channel_info.cha_info.monmax # query channel  month max
            

            cp_list = g.session.query(UsrChannel).filter(UsrChannel.channelid== channel_id).filter(UsrChannel.is_show == True).all()
            _kill_bl = 0
            if cp_list:
                cp = random.sample(cp_list, 1)
                channel_province_day_max = get_channel_province_count(cp[0].id, cp[0].cpid, mobile_info.province) #query province count.
                channel_province_all_count = get_channel_count(channel_id, cp[0].cpid, mobile_info.province) # query channel_count 
                channel_province_kill_count = get_channel_count(channel_id, cp[0].cpid, mobile_info.province,  1) # kill data
                channel_province_no_kill_count = get_channel_count(channel_id, cp[0].cpid, mobile_info.province,  0) # no kill data
                channel_province_black_province_count = get_channel_count(channel_id, cp[0].cpid, mobile_info.province,  2) # black province data
                channel_province_black_mobile_count = get_channel_count(channel_id, cp[0].cpid, mobile_info.province,  3) # black mobile data

                _kill_bl = cp[0].bl
                data_mr.cpid = cp[0].cpid

            if day_count >= channel_day_max and channel_day_max > 0:
                is_kill = True

            if month_count >= channel_month_max and channel_month_max > 0:
                is_kill = True

            if channel_province_all_count >= channel_province_day_max and channel_province_day_max > 0:
                is_kill = True
            print "=============all_count"
            print channel_province_all_count
            print channel_province_black_mobile_count
            print channel_province_black_province_count
            print channel_province_no_kill_count
            if not is_kill and channel_province_all_count >0:
                kill_count = channel_province_all_count - channel_province_black_mobile_count - channel_province_black_province_count - channel_province_no_kill_count
                print "=============kill_count"
                print kill_count
                if kill_count > 0:
                    if (channel_province_all_count / kill_count) < 2:
                        is_kill = True
                        print '=================is kill============='
                    else:
                        print '=================no kill============='

            data_mr.channelid = channel_id
            data_mr.spnumber = spnumber
            data_mr.price = channel_info.cha_info.price
            data_mr.linkid = linkid
            data_mr.province = mobile_info.province
            data_mr.city = mobile_info.city
            today = datetime.datetime.today()
            data_mr.regdate = "%s%s%s" % (today.year, today.month, today.day)
            data_mr.reghour = today.hour
            data_mr.state = True
            data_mr.is_kill = is_kill
            data_mr.create_time = datetime.datetime.now()
            
            sp_log = UsrSPTongLog()
            sp_log.channelid = channel_id
            sp_log.spid = SP_ID
            sp_log. urltype = 2
            sp_log.mobile = mobile
            sp_log.spnumber = spnumber
            sp_log.momsg = spnumber
            sp_log.linkid = linkid
            sp_log.tongurl = request.url
            sp_log.is_show = True
            sp_log.tongdate = "%s%s%s" % (today.year, today.month, today.day)
            sp_log.create_time = datetime.datetime.now()
            try:
                g.session.add(data_mr)
                g.session.add(sp_log)
                g.session.commit()
                return jsonify({'ok': True}) 
            except Exception, e:
                return jsonify({'ok': False})
            # query mobile attribution
            # query channel sync count
            #  计算是否扣量
            # INSERT OR UPDATE DATA_MO
            # if not  is_kill
            # sync CP data.

        return jsonify({'ok': False})

    return jsonify({'ok': False, 'SP_ID': SP_ID, 'MSG': 'The SP IS UNDEFINED'})
