# -*- coding: utf-8 -*-

import datetime
import time
import urllib2, urllib
import simplejson
import os
import sys
import md5
import random
import math

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
                get_channel_province_count, get_channel_count, get_mobile_city_block

operator_view = Blueprint('operator_view', __name__)

@operator_view.route('/MO/TEST/', methods=["GET", "POST"])
def MO_TEST():
  return "OK"

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

            cp_list = g.session.query(UsrChannel).filter(UsrChannel.channelid== channel_id).\
                            filter(UsrChannel.spnumber==spnumber).\
                            filter(UsrChannel.momsg==msg).\
                            filter(UsrChannel.is_show == True).first()
            if cp_list:
                cp = cp_list
                data_mo.cpid = cp.cpid

            data_mo.channelid = channel_id
            data_mo.spnumber = spnumber
            data_mo.price = channel_info.cha_info.price
            data_mo.linkid = linkid
            data_mo.province = mobile_info.province
            data_mo.city = mobile_info.city
            today = datetime.datetime.today()
            _month = today.month if today.month >= 10 else "0%s" % today.month
            _day = today.day if today.day >= 10 else "0%s"  % today.day
            data_mo.regdate = "%s%s%s" % (today.year, _month, _day)
            data_mo.reghour = today.hour
            data_mo.create_time = datetime.datetime.now()

            ever_day = g.session.query(DataEverday).filter(DataEverday.channelid==channel_id).\
                            filter(DataEverday.cpid==data_mo.cpid).\
                            filter(DataEverday.province==data_mo.province).\
                            filter(DataEverday.city == data_mo.city).\
                            filter(DataEverday.tj_hour==data_mo.reghour).first()

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
                g.session.close()
                return "OK"
            except Exception, e:
                return "ERROR"
            # query mobile attribution
            # query channel sync count
            #  计算是否扣量
            # INSERT OR UPDATE DATA_MO
            # if not  is_kill
            # sync CP data.

        return "ERROR"

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
            status = req.get(channel_info.status_name, None)
            status_val = channel_info.status_val
            type_name = req.get(channel_info.type_name, None)
            type_val = channel_info.type_key

            if channel_info.status_name:
                status_name = req.get(channel_info.status_name, '')
                status_val = channel_info.status_val

            if channel_info.type_name:
                type_name = req.get(channel_info.type_name, '')
                type_key = channel_info.spnumber

            mobile_mo = g.session.query(DataMo).filter(DataMo.linkid==linkid).filter(DataMo.channelid==channel_id).first()
            if not mobile and mobile_mo:
                if mobile_mo:
                    mobile = mobile_mo.mobile

            if not msg and mobile_mo:
                msg = mobile_mo.momsg

            if not spnumber and mobile_mo:
                spnumber = mobile_mo.spnumber

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
            is_city_block = get_mobile_city_block(mobile_info.city, mobile_info.province, channel_id) #查询所在城市是否是屏蔽状态

            #cp_list = g.session.query(UsrChannel).filter(UsrChannel.channelid== channel_id).filter(UsrChannel.is_show == True).all()
            cp_list = g.session.query(UsrChannel).filter(UsrChannel.channelid== channel_id).\
                            filter(UsrChannel.spnumber==spnumber).\
                            filter(UsrChannel.momsg==msg).\
                            filter(UsrChannel.is_show == True).first()
            _kill_bl = 0 #扣量比列
            kill_val = 0 #扣量代码： 0不扣量，1计算比列扣量， 2省份屏蔽扣量， 3 黑名单扣量
            if cp_list:
                cp = cp_list
                channel_province_day_max = get_channel_province_count(cp.id, cp.cpid, mobile_info.province) # 查询渠道分配的省份日限数量
                channel_province_all_count = get_channel_count(channel_id, cp.cpid, mobile_info.province) # 查询该省份今日产生的流量总和
                channel_province_kill_count = get_channel_count(channel_id, cp.cpid, mobile_info.province,  1) # 查询该省份今日扣量的总和
                channel_province_no_kill_count = get_channel_count(channel_id, cp.cpid, mobile_info.province,  0) # 查询该渠道省份正常下发的总和
                channel_province_black_province_count = get_channel_count(channel_id, cp.cpid, mobile_info.province,  2) # 查询该渠道省份屏蔽地市的流量总和
                channel_province_black_mobile_count = get_channel_count(channel_id, cp.cpid, mobile_info.province,  3) # 查询该渠道省份黑名单流量总和
                req_url = cp.backurl
                _kill_bl = cp.bl
                data_mr.cpid = cp.cpid
            else:
                is_kill = True
                kill_val = 1

            if day_count >= channel_day_max and channel_day_max > 0:
                is_kill = True
                kill_val = 1
            if month_count >= channel_month_max and channel_month_max > 0:
                is_kill = True
                kill_val = 1
            if channel_province_all_count >= channel_province_day_max and channel_province_day_max > 0:
                is_kill = True
                kill_val = 1
            if is_block:
                is_kill = True
                kill_val = 3

            if not is_city_block:
                is_kill = True
                kill_val = 2

            if not is_kill and channel_province_all_count >0:
                
                #
                #扣量=总MR-黑名单-下发数据-屏蔽地区
                #扣量比例 = 100 - 同步给渠道的总MR数据/（总MR数据 - 黑名单 - 屏蔽地区）
                #
                ALL_COUNT = channel_province_all_count
                SEND_COUNT = channel_province_no_kill_count
                RM_COUNT = channel_province_black_province_count
                BLACK_COUNT = channel_province_black_mobile_count
                CHANNEL_COUNT = (float(ALL_COUNT) - float(RM_COUNT) - float(BLACK_COUNT))
                if CHANNEL_COUNT > 0:
                    kill_count = float(SEND_COUNT) / CHANNEL_COUNT
                    kill_count = kill_count * 100
                else:
                    kill_count = 0

                if kill_count > 0:
                    if (int(_kill_bl)+kill_count) > 100:
                        kill_val = 1
                        is_kill = True

            data_mr.channelid = channel_id
            data_mr.spnumber = spnumber
            data_mr.price = channel_info.cha_info.price
            data_mr.linkid = linkid
            data_mr.province = mobile_info.province
            data_mr.city = mobile_info.city
            today = datetime.datetime.today()
            _month = today.month if today.month >= 10 else "0%s" % today.month
            _day = today.day if today.day >= 10 else "0%s" %  today.day
            data_mr.regdate = "%s%s%s" % (today.year, _month, _day)
            data_mr.reghour = today.hour
            if status:
                #status = req.get(channel_info.status_name, None)
                #status_val = channel_info.status_val
                #type_name = req.get(channel_info.type_name, None)
                #type_val = channel_info.type_key
                if status == status_val:
                    data_mr.state = True
                else:
                    data_mr.state = False
            else:
                if type_name:
                    if type_name == type_val:
                        data_mr.state = True
                    else:
                        data_mr.state = False
                else:
                    data_mr.state = True
            data_mr.is_kill = kill_val
            data_mr.create_time = datetime.datetime.now()
            if not data_mr.state:
                kill_val = 4
                is_kill = False

            if not is_kill:
                cp_log = UsrCPTongLog()
                cp_log.channelid = channel_id
                cp_log.cpid = data_mr.cpid
                cp_log.urltype = 2
                cp_log.mobile = mobile
                cp_log.spnumber = spnumber
                cp_log.momsg = msg
                cp_log.linkid = linkid              

                cp_log.tongdate = "%s%s%s" % (today.year, today.month, today.day)
                cp_log.create_time = datetime.datetime.now()
                values = {'msg' : msg,
                    'spcode': spnumber,
                    'mobile': mobile,
                    'linkid': linkid,
                    'channelid': channel_id
                }
                data = urllib.urlencode(values)
                req = "%s?%s" % (req_url, data)

                cp_log.tongurl = req

                try:
                    if req_url:
                        response = urllib.urlopen(req)
                        data = response.read()
                        cp_log.backmsg = data
                        data_mr.state = True
                    else:
                        data_mr.state = False
                        cp_log.backmsg = 'OK'
                except Exception, e:
                    cp_log.backmsg = 'ERROR'

                g.session.add(cp_log)

            sp_log = UsrSPTongLog()
            sp_log.channelid = channel_id
            sp_log.spid = SP_ID
            sp_log.urltype = 2
            sp_log.mobile = mobile
            sp_log.spnumber = spnumber
            sp_log.momsg = msg
            sp_log.linkid = linkid
            sp_log.tongurl = request.url
            sp_log.is_show = data_mr.state
            sp_log.tongdate = "%s%s%s" % (today.year, today.month, today.day)
            sp_log.create_time = datetime.datetime.now()

            ever_day = g.session.query(DataEverday).filter(DataEverday.channelid==channel_id).\
                filter(DataEverday.cpid==data_mr.cpid).\
                filter(DataEverday.province==data_mr.province).\
                filter(DataEverday.city == data_mr.city).\
                filter(DataEverday.tj_hour==data_mr.reghour).first()

            if ever_day:
                ever_day.mr_all += 1
                if not is_kill:
                  ever_day.mr_cp += 1
                ever_day.datetime = datetime.datetime.now()
            else:
                ever_day = DataEverday()
                ever_day.channelid = channel_id
                ever_day.cpid = data_mr.cpid
                ever_day.price = data_mr.price
                ever_day.province = data_mr.province
                ever_day.city = data_mr.city
                ever_day.tj_hour = data_mr.reghour
                ever_day.mo_all = 0
                ever_day.mr_all = 1
                if not is_kill:
                  ever_day.mr_cp = 1
                else:
                  ever_day.mr_cp = 0
                ever_day.tj_date = data_mr.regdate
                ever_day.create_time = datetime.datetime.now()

            try:
                g.session.add(data_mr)
                g.session.add(sp_log)
                g.session.add(ever_day)
                g.session.commit()
                g.session.close()
                return "OK"
            except Exception, e:
                g.session.rollback()
                return "ERROR"
            # query mobile attribution
            # query channel sync count
            #  计算是否扣量
            # INSERT OR UPDATE DATA_MO
            # if not  is_kill
            # sync CP data.

        return "ERROR"

    return jsonify({'ok': False, 'SP_ID': SP_ID, 'MSG': 'The SP IS UNDEFINED'})
