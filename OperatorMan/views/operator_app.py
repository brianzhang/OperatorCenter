# -*- coding: utf-8 -*-

import datetime
import calendar
import time
import urllib2, urllib
import simplejson as json
import os
import sys
import md5
import math
reload(sys)
sys.setdefaultencoding("utf-8")

from sqlalchemy import or_, desc, func, distinct, CHAR, sql
from sqlalchemy.orm import subqueryload

from datetime import timedelta
from flask import request, render_template, jsonify, g, Blueprint, Response, redirect, session, url_for
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
import flask.ext.wtf as wtf

from werkzeug import secure_filename
from OperatorMan.configs import settings
from OperatorMan.views import ok_json, fail_json, hash_password, write_sys_log, random_key, get_send_html, \
                query_stats_data, query_province_stats, query_channel_status
from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync

from OperatorMan.utils import User

operator_view = Blueprint('operator_view', __name__, url_prefix='/operator')


@operator_view.route("/status/", methods=['GET', 'POST'])
@login_required
def operator_status():
    '''
    状态报告-> CP的数据
    '''
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        provinces = g.session.query(PubProvince).all()
        users = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()
        today = datetime.datetime.today()
        _month = today.month if today.month >= 10 else "0%s" % today.month
        _day = today.day if today.day >= 10 else "0%s" %  today.day
        curr_date = "%s-%s-%s" % (today.year, _month, _day)
        return  render_template('operator_status.html', channels=channels,
                                                        cp_info_list=cp_info_list,
                                                        provinces=provinces,
                                                        users=users,
                                                        random_key = random_key(),
                                                        curr_date = curr_date)
    else:
        operator_list = g.session.query(DataMr).order_by(desc(DataMr.id))
        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        cpinfo = req.get('cpinfo', None)
        provinces = req.get('provinces', None)
        is_kill = req.get('is_kill', None)
        status = req.get('status', None)
        users = req.get('users', None)
        types = req.get('types', None)
        query_value = req.get('values', None)
        stmt = g.session.query(func.count(DataMr.id).label("cp_count")).filter(DataMr.is_kill==0).filter(DataMr.state==True)
        
        stats_query = g.session.query(func.count(distinct(DataMr.channelid)).label('channel_count'), \
                                    func.count(distinct(DataMr.mobile)).label('mobile_count'),\
                                    func.count(DataMr.id).label('id_count'),\
                                    func.count(DataMr.state).label('status')
                                    )

        if start_time:
            start_time += ' 00:00:00'
            operator_list = operator_list.filter(DataMr.create_time >= start_time)
            stats_query = stats_query.filter(DataMr.create_time >= start_time)
            stmt = stmt.filter(DataMr.create_time >= start_time)
        if end_time:
            end_time += ' 23:59:59'
            operator_list = operator_list.filter(DataMr.create_time <= end_time)
            stats_query = stats_query.filter(DataMr.create_time <= end_time)
            stmt = stmt.filter(DataMr.create_time <= end_time)
        else:
            today = datetime.datetime.today()
            _month = today.month if today.month >= 10 else "0%s" % today.month
            _day = today.day if today.day >= 10 else "0%s" %  today.day
            regdate = "%s%s%s" % (today.year, _month, _day)

            operator_list = operator_list.filter(DataMr.regdate == regdate)
            stats_query = stats_query.filter(DataMr.regdate == regdate)
            stmt = stmt.filter(DataMr.regdate == regdate)

        if channel:
            operator_list = operator_list.filter(DataMr.channelid == channel)
            stats_query = stats_query.filter(DataMr.channelid == channel)
            stmt = stmt.filter(DataMr.channelid == channel)
        if cpinfo:
            operator_list = operator_list.filter(DataMr.cpid == cpinfo)
            stats_query = stats_query.filter(DataMr.cpid == cpinfo)
            stmt = stmt.filter(DataMr.cpid == cpinfo)
        if provinces:
            operator_list = operator_list.filter(DataMr.province == provinces)
            stats_query = stats_query.filter(DataMr.province == provinces)
            stmt = stmt.filter(DataMr.province == province)
        if is_kill:
            operator_list = operator_list.filter(DataMr.is_kill == is_kill)
            stats_query = stats_query.filter(DataMr.is_kill == is_kill)
            stmt = stmt.filter(DataMr.is_kill == is_kill)
        if status:
            operator_list = operator_list.filter(DataMr.state == status)
            stats_query = stats_query.filter(DataMr.state == status)
            stmt = stmt.filter(DataMr.state == status)
        if users:
            operator_list = operator_list.filter(UsrCPInfo.adminid == users)
            stats_query = stats_query.filter(UsrCPInfo.adminid == users)
            stmt = stmt.filter(UserCPInfo.adminid == users)
        if types and query_value:
           if types == 'Mobile':
               operator_list = operator_list.filter(DataMr.mobile == query_value)
               stats_query = stats_query.filter(DataMr.mobile == query_value)
               stmt = stmt.filter(DataMr.mobile == query_value)
           if types == "SX":
               operator_list = operator_list.filter(DataMr.momsg == query_value)
               stats_query = stats_query.filter(DataMr.momsg == query_value)
               stmt = stmt.filter(DataMr.momsg == query_value)
           if types == 'SPNumber':
               operator_list = operator_list.filter(DataMr.spnumber == query_value)
               stats_query = stats_query.filter(DataMr.spnumber == query_value)
               stmt = stmt.filter(DataMr.spunmber == query_value)
           if types == 'City':
               _city = g.session.query(PubCity).filter(PubCity.city==query_value).first()
               if _city:
                   operator_list = operator_list.filter(DataMr.city == _city.id)
                   stats_query = stats_query.filter(DataMr.city == _city.id)
                   stmt = stmt.filter(DataMr.city == _city.id)
           if types == 'LinkID':
               operator_list = operator_list.filter(DataMr.linkid == query_value)
               stats_query = stats_query.filter(DataMr.linkid == query_value)
               stmt = stmt.filter(DataMr.linkid == query_value)
        #if
        #query_data.add_column(DataEverday.tj_hour.label('has_index'))
        #stmt.c.cp_count.label("cp_count")
        #.subquery()
        stmt = stmt.subquery()
        stats_query = stats_query.add_column(stmt.c.cp_count.label("cp_count"))
        stats_query = stats_query.first()

        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        start = math.fabs(start)
        total = 0
        stats_data = {}
        if stats_query:
            stats_data['id_count'] = stats_query.id_count
            stats_data['channel_count'] = stats_query.channel_count
            stats_data['mobile_count'] = stats_query.mobile_count
            stats_data['status'] = stats_query.status
            stats_data['cp_count'] = stats_query.cp_count
            stats_data['error_count'] = stats_query.id_count - stats_query.status
            total = stats_query.id_count

        operator_list = operator_list.offset(start).limit(numperpage).all()
        #operator_list = operator_list[start:(numperpage+start)]
        if operator_list:
            operator_data = []
            for item in operator_list:
                operator_data.append({'sp': "[%s]%s" % (item.channe_info.sp_info.id, item.channe_info.sp_info.name),
                                    'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                    'mobile': item.mobile,
                                    'momsg':  "%s %s" % (item.momsg, u'分钟' if item.is_ivr else ''),
                                    'linkid': item.linkid,
                                    'spnumber': item.spnumber,
                                    'city': "%s-%s" % (item.provinces.province, item.citys.city),
                                    'cp': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
                                    'create_time': item.create_time,
                                    'status': item.state,
                                    'is_kill': get_send_html(item.state, item.is_kill),
                                    'id': item.id})

            return jsonify({'rows': operator_data, 'total': total, 'stats_data': stats_data})
        else:
            return jsonify({'rows': [], 'total': 0})


@operator_view.route("/sync/", methods=['GET', 'POST'])
@login_required
def operator_sync():
    '''
    状态报告-> CP的数据
    '''
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        provinces = g.session.query(PubProvince).all()
        users = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()
        today = datetime.datetime.today()
        _month = today.month if today.month >= 10 else "0%s" % today.month
        _day = today.day if today.day >= 10 else "0%s" %  today.day
        curr_date = "%s-%s-%s" % (today.year, _month, _day)
        return  render_template('operator_sync.html', channels=channels,
                                                        cp_info_list=cp_info_list,
                                                        provinces=provinces,
                                                        users=users,
                                                        random_key = random_key(),
                                                        curr_date = curr_date)
    else:
        operator_list = g.session.query(DataMr).order_by(desc(DataMr.id))
        operator_list = operator_list.filter(or_(DataMr.is_kill == 0, DataMr.is_kill == 5, DataMr.is_kill == -1))
        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        cpinfo = req.get('cpinfo', None)
        provinces = req.get('provinces', None)
        is_kill = req.get('is_kill', None)
        status = req.get('status', None)
        users = req.get('users', None)
        types = req.get('types', None)
        query_value = req.get('values', None)
        stmt = g.session.query(func.count(DataMr.id).label("cp_count")).filter(DataMr.is_kill==0).filter(DataMr.state==True)
        
        stats_query = g.session.query(func.count(distinct(DataMr.channelid)).label('channel_count'), \
                                    func.count(distinct(DataMr.mobile)).label('mobile_count'),\
                                    func.count(DataMr.id).label('id_count'),\
                                    func.count(DataMr.state).label('status')
                                    )

        if start_time:
            start_time += ' 00:00:00'
            operator_list = operator_list.filter(DataMr.create_time >= start_time)
            stats_query = stats_query.filter(DataMr.create_time >= start_time)
            stmt = stmt.filter(DataMr.create_time >= start_time)
        if end_time:
            end_time += ' 23:59:59'
            operator_list = operator_list.filter(DataMr.create_time <= end_time)
            stats_query = stats_query.filter(DataMr.create_time <= end_time)
            stmt = stmt.filter(DataMr.create_time <= end_time)
        else:
            today = datetime.datetime.today()
            _month = today.month if today.month >= 10 else "0%s" % today.month
            _day = today.day if today.day >= 10 else "0%s" %  today.day
            regdate = "%s%s%s" % (today.year, _month, _day)

            operator_list = operator_list.filter(DataMr.regdate == regdate)
            stats_query = stats_query.filter(DataMr.regdate == regdate)
            stmt = stmt.filter(DataMr.regdate == regdate)

        if channel:
            operator_list = operator_list.filter(DataMr.channelid == channel)
            stats_query = stats_query.filter(DataMr.channelid == channel)
            stmt = stmt.filter(DataMr.channelid == channel)
        if cpinfo:
            operator_list = operator_list.filter(DataMr.cpid == cpinfo)
            stats_query = stats_query.filter(DataMr.cpid == cpinfo)
            stmt = stmt.filter(DataMr.cpid == cpinfo)
        if provinces:
            operator_list = operator_list.filter(DataMr.province == provinces)
            stats_query = stats_query.filter(DataMr.province == provinces)
            stmt = stmt.filter(DataMr.province == province)
        if is_kill:
            operator_list = operator_list.filter(DataMr.is_kill == is_kill)
            stats_query = stats_query.filter(DataMr.is_kill == is_kill)
            stmt = stmt.filter(DataMr.is_kill == is_kill)
        if status:
            operator_list = operator_list.filter(DataMr.state == status)
            stats_query = stats_query.filter(DataMr.state == status)
            stmt = stmt.filter(DataMr.state == status)
        if users:
            operator_list = operator_list.filter(UsrCPInfo.adminid == users)
            stats_query = stats_query.filter(UsrCPInfo.adminid == users)
            stmt = stmt.filter(UserCPInfo.adminid == users)
        if types and query_value:
           if types == 'Mobile':
               operator_list = operator_list.filter(DataMr.mobile == query_value)
               stats_query = stats_query.filter(DataMr.mobile == query_value)
               stmt = stmt.filter(DataMr.mobile == query_value)
           if types == "SX":
               operator_list = operator_list.filter(DataMr.momsg == query_value)
               stats_query = stats_query.filter(DataMr.momsg == query_value)
               stmt = stmt.filter(DataMr.momsg == query_value)
           if types == 'SPNumber':
               operator_list = operator_list.filter(DataMr.spnumber == query_value)
               stats_query = stats_query.filter(DataMr.spnumber == query_value)
               stmt = stmt.filter(DataMr.spunmber == query_value)
           if types == 'City':
               _city = g.session.query(PubCity).filter(PubCity.city==query_value).first()
               if _city:
                   operator_list = operator_list.filter(DataMr.city == _city.id)
                   stats_query = stats_query.filter(DataMr.city == _city.id)
                   stmt = stmt.filter(DataMr.city == _city.id)
           if types == 'LinkID':
               operator_list = operator_list.filter(DataMr.linkid == query_value)
               stats_query = stats_query.filter(DataMr.linkid == query_value)
               stmt = stmt.filter(DataMr.linkid == query_value)
        #if
        #query_data.add_column(DataEverday.tj_hour.label('has_index'))
        #stmt.c.cp_count.label("cp_count")
        #.subquery()
        stmt = stmt.subquery()
        stats_query = stats_query.add_column(stmt.c.cp_count.label("cp_count"))
        stats_query = stats_query.first()

        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        start = math.fabs(start)
        total = 0
        stats_data = {}
        if stats_query:
            stats_data['id_count'] = stats_query.id_count
            stats_data['channel_count'] = stats_query.channel_count
            stats_data['mobile_count'] = stats_query.mobile_count
            stats_data['status'] = stats_query.status
            stats_data['cp_count'] = stats_query.cp_count
            stats_data['error_count'] = stats_query.id_count - stats_query.status
            total = stats_query.id_count

        operator_list = operator_list.offset(start).limit(numperpage).all()
        #operator_list = operator_list[start:(numperpage+start)]
        if operator_list:
            operator_data = []
            for item in operator_list:
                operator_data.append({'sp': "[%s]%s" % (item.channe_info.sp_info.id, item.channe_info.sp_info.name),
                                    'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                    'mobile': item.mobile,
                                    'momsg':  "%s %s" % (item.momsg, u'分钟' if item.is_ivr else ''),
                                    'linkid': item.linkid,
                                    'spnumber': item.spnumber,
                                    'city': "%s-%s" % (item.provinces.province, item.citys.city),
                                    'cp': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
                                    'create_time': item.create_time,
                                    'status': item.state,
                                    'is_kill': get_send_html(item.state, item.is_kill),
                                    'id': item.id})

            return jsonify({'rows': operator_data, 'total': total, 'stats_data': stats_data})
        else:
            return jsonify({'rows': [], 'total': 0})

@operator_view.route("/sync/data/", methods=['POST'])
@login_required
def operator_sync_stat():
    '''
    状态报告-> CP的数据
    '''
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'POST':
        id_data=  req.getlist('ids[]', None)
        sync_count = 0
        sync_status = 0
        for mr_id in id_data:
            sync_count += 1
            data_mr = g.session.query(DataMr).filter(DataMr.id==mr_id).first()
            cp_info = g.session.query(UsrChannel).filter(UsrChannel.channelid== data_mr.channelid).\
                            filter(UsrChannel.is_show == True).filter(UsrChannel.cpid == data_mr.cpid).first()

            if not data_mr and not cp_info:
                continue

            req_url = cp_info.backurl
            cp_log = UsrCPTongLog()
            cp_log.channelid = data_mr.channelid
            cp_log.cpid = data_mr.cpid
            cp_log.urltype = 2
            cp_log.mobile = data_mr.mobile
            cp_log.spnumber = data_mr.spnumber
            cp_log.momsg = data_mr.momsg
            cp_log.linkid = data_mr.linkid

            cp_log.tongdate = datetime.datetime.now()
            cp_log.create_time = datetime.datetime.now()
            values = {'msg' : data_mr.momsg,
                'spcode': data_mr.spnumber,
                'mobile': data_mr.mobile,
                'linkid': data_mr.linkid,
                'channelid': data_mr.channelid
            }
            if data_mr.is_ivr:
                values['duration']=data_mr.momsg

            if req_url:
                data = urllib.urlencode(values)
                req = "%s?%s" % (req_url, data)

                cp_log.tongurl = req

                try:
                    if req_url:
                        response = urllib.urlopen(req)
                        data = response.read()
                        cp_log.backmsg = data
                        data_mr.is_kill = 0
                        sync_status += 1
                    else:
                        data_mr.is_kill = -1
                        cp_log.backmsg = 'OK'
                except Exception, e:
                    data_mr.is_kill = -1
                    cp_log.backmsg = 'ERROR'
            else:
                data_mr.is_kill = 5
                data = urllib.urlencode(values)
                req = "%s?%s" % (req_url, data)
                cp_log.tongurl = req
                cp_log.backmsg = 'ERROR'

            g.session.add(cp_log)
            g.session.add(data_mr)
        try:
            g.session.commit()
        except Exception, e: 
            return jsonify({'ok': False})
        return jsonify({'ok': True, 'data': u"同步完成,总共同步: %s条, 成功: %s条, 失败: %s条" % (sync_count, sync_status, (sync_count - sync_status))})
    else:
        return jsonify({'ok': False})

@operator_view.route("/demand/", methods=['GET', 'POST'])
@login_required
def operator_demand():
    '''
    点播上行--> SP 的数据信息
    '''
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        provinces = g.session.query(PubProvince).all()
        users = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()
        today = datetime.datetime.today()
        _month = today.month if today.month >= 10 else "0%s" % today.month
        _day = today.day if today.day >= 10 else "0%s" %  today.day
        curr_date = "%s-%s-%s" % (today.year, _month, _day)
        return  render_template('operator_demand.html', channels=channels,
                                                        cp_info_list=cp_info_list,
                                                        provinces=provinces,
                                                        users=users,
                                                        random_key=random_key(),
                                                        curr_date=curr_date)
    else:
        operator_list = g.session.query(DataMo).order_by(desc(DataMo.id))
        #operator_list = operator_list.filter(ChaInfo.busi_type == 3)
        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        cpinfo = req.get('cpinfo', None)
        provinces = req.get('provinces', None)
        is_kill = req.get('is_kill', None)
        status = req.get('status', None)
        users = req.get('users', None)
        types = req.get('types', None)
        order = req.get('order', None)
        if start_time:
            start_time += ' 00:00:00'
            operator_list = operator_list.filter(DataMo.create_time >= start_time)
        if end_time:
            end_time += ' 23:59:59'
            operator_list = operator_list.filter(DataMo.create_time <= end_time)
        else:
            today = datetime.datetime.today()
            _month = today.month if today.month >= 10 else "0%s" % today.month
            _day = today.day if today.day >= 10 else "0%s" %  today.day
            regdate = "%s%s%s" % (today.year, _month, _day)

            operator_list = operator_list.filter(DataMo.regdate == regdate)

        if channel:
            operator_list = operator_list.filter(DataMo.channelid == channel)
        if cpinfo:
            operator_list = operator_list.filter(DataMo.cpid == cpinfo)
        if provinces:
            operator_list = operator_list.filter(DataMo.province == provinces)
        #if
        operator_list = operator_list.all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(operator_list)
        operator_list = operator_list[start:(numperpage+start)]
        print operator_list
        if operator_list:
            operator_data = []
            for item in operator_list:
                operator_data.append({'sp': "[%s]%s" % (item.channe_info.sp_info.id, item.channe_info.sp_info.name),
                                    'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                    'mobile': item.mobile,
                                    'momsg': item.momsg,
                                    'linkid': item.linkid,
                                    'spnumber': item.spnumber,
                                    'city': "%s-%s" % (item.provinces.province, item.citys.city),
                                    'cp': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
                                    'create_time': item.create_time
                                    })

            return jsonify({'rows': operator_data, 'total': total})
        else:
            return jsonify({'rows': [], 'total': 0})

@operator_view.route("/exploits/", methods=['GET', 'POST'])
@login_required
def operator_exploits():
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        today = datetime.datetime.today()
        _month = today.month if today.month >= 10 else "0%s" % today.month
        _day = today.day if today.day >= 10 else "0%s" %  today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        data = query_stats_data(req)

        return render_template('operator_exploits.html',channels=channels,
                                                        sp_info_list=sp_info_list,
                                                        query_type='time',
                                                        render_data=json.dumps(data),
                                                        regdate=regdate,
                                                        random_key = random_key()
                                                        )
    else:
        data = query_stats_data(req)
        return jsonify(data)

@operator_view.route("/region/", methods=['GET', 'POST'])
@login_required
def operator_region():
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        today = datetime.datetime.today()
        _month = today.month if today.month >= 10 else "0%s" % today.month
        _day = today.day if today.day >= 10 else "0%s" %  today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        data = query_province_stats(req)
        return render_template('operator_region.html',channels=channels,
                                                        sp_info_list=sp_info_list,
                                                        query_type='time',
                                                        regdate= regdate,
                                                        data = json.dumps(data),
                                                        random_key = random_key()
                                                        )
    else:
        data = query_province_stats(req)
        return jsonify(data)

@operator_view.route("/purpose/", methods=['GET', 'POST'])
@login_required
def operator_purpose():
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        today = datetime.datetime.today()
        _month = today.month if today.month >= 10 else "0%s" % today.month
        _day = today.day if today.day >= 10 else "0%s" %  today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)
        data = query_channel_status(req)
        return render_template('operator_purpose.html', regdate=regdate, data=json.dumps(data), random_key = random_key())
    else:
        data = query_channel_status(req)
        return jsonify(data)

