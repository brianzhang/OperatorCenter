# -*- coding: utf-8 -*-

import datetime
import calendar
import time
import urllib2, urllib
import simplejson as json
import os
import sys
import md5

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
from OperatorMan.views import ok_json, fail_json, hash_password, write_sys_log, random_key
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

        return  render_template('operator_status.html', channels=channels,
                                                        cp_info_list=cp_info_list,
                                                        provinces=provinces,
                                                        users=users,
                                                        random_key = random_key())
    else:
        operator_list = g.session.query(DataMr).order_by(desc(DataMr.id))
        operator_list = operator_list.filter(ChaInfo.busi_type != 3)
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
            start_time += '00:00:00'
            operator_list = operator_list.filter(DataMr.create_time >= start_time)
        if end_time:
            end_time += '00:00:00'
            operator_list = operator_list.filter(DataMr.create_time <= end_time)
        else:
            today = datetime.datetime.today()
            _month = today.month if today.month >= 10 else "0%s" % today.month
            _day = today.day if today.day >= 10 else "0%s" %  today.day
            regdate = "%s%s%s" % (today.year, _month, _day)

            operator_list = operator_list.filter(DataMr.regdate == regdate)
        if channel:
            operator_list = operator_list.filter(DataMr.channelid == channel)
        if cpinfo:
            operator_list = operator_list.filter(DataMr.cpid == cpinfo)
        if provinces:
            operator_list = operator_list.filter(DataMr.province == provinces)
        if is_kill:
            operator_list = operator_list.filter(DataMr.is_kill == is_kill)
        if status:
            operator_list = operator_list.filter(DataMr.state == status)
        #if
        operator_list = operator_list.all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(operator_list)
        operator_list = operator_list[start:(numperpage+start)]
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
                                    'create_time': item.create_time,
                                    'status': item.state,
                                    'is_kill': item.is_kill,
                                    'id': item.id})

            return jsonify({'rows': operator_data, 'total': total})
        else:
            return jsonify({'rows': [], 'total': 0})

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

        return  render_template('operator_demand.html', channels=channels,
                                                        cp_info_list=cp_info_list,
                                                        provinces=provinces,
                                                        users=users,
                                                        random_key=random_key())
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
            start_time += '00:00:00'
            operator_list = operator_list.filter(DataMo.create_time >= start_time)
        if end_time:
            end_time += '00:00:00'
            operator_list = operator_list.filter(DataMo.create_time <= end_time)
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
        _month = today.month if today.month >10 else '0%s' % today.month
        _day = today.day if today.day >10 else '0%s' % today.day
        regdate = "%s%s%s" % (today.year, _month, _day)
        query_data = g.session.query(DataEverday.tj_hour, func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp')).\
                                    filter(DataEverday.tj_date ==regdate).group_by(DataEverday.tj_hour).all()

        user_count = g.session.query(DataMr.reghour, func.count(distinct(DataMr.mobile)).label('user_count')).filter(DataMr.regdate==regdate).group_by(DataMr.reghour).all()

        t_customize = range(1, 24)
        t_conversion_rate = range(1, 24)
        conversion_rate = range(1, 24)
        into_rate = range(1, 24)
        arpu = range(1, 24)
        for i in range(0, 23):
            t_customize[i] = 0
            t_conversion_rate[i] = 0
            conversion_rate[i] = 0
            into_rate[i] = 0
            arpu[i] = 0

        if query_data:
            data_list = {}
            for item in query_data:
                t_customize[item.tj_hour-1] = item.mr_all
                item.mo_all = item.mo_all if item.mo_all > 0 else 1
                item.mr_all = item.mr_all if item.mr_all > 0 else 1
                t_conversion_rate[item.tj_hour-1] = float(item.mr_all) / float(item.mo_all)
                t_conversion_rate[item.tj_hour-1] = float("%.2f" % t_conversion_rate[item.tj_hour-1])
                conversion_rate[item.tj_hour-1] = float(item.mr_cp) / float(item.mr_all)
                conversion_rate[item.tj_hour-1] = float("%.2f" % conversion_rate[item.tj_hour-1])
                into_rate[item.tj_hour-1] = float(item.mr_cp) / float(item.mr_all)
                into_rate[item.tj_hour-1] = float("%.2f" % into_rate[item.tj_hour-1])
                for u in user_count:
                    if u.reghour == item.tj_hour:
                        arpu[item.tj_hour-1] = float(u.user_count) / float(item.mr_all)
                        arpu[item.tj_hour-1] = float("%.2f" % arpu[item.tj_hour-1])

        return render_template('operator_exploits.html',channels=channels,
                                                        sp_info_list=sp_info_list,
                                                        query_type='time',
                                                        t_customize = json.dumps(t_customize),
                                                        t_conversion_rate = json.dumps(t_conversion_rate),
                                                        conversion_rate = json.dumps(conversion_rate),
                                                        into_rate = json.dumps(into_rate),
                                                        arpu = json.dumps(arpu),
                                                        regdate=regdate,
                                                        random_key = random_key()
                                                        )
    else:
        order_type = req.get('order_type', None)
        time = req.get('time', None)
        month = req.get('month', None)
        year = req.get('year', None)
        channelid = req.get('channel_id', None)
        sp_id = req.get("sp_id", None)
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s%s%s" % (today.year, _month, _day)

        query_data = g.session.query(func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp'))

        user_count = g.session.query(DataMr.reghour, func.count(distinct(DataMr.mobile)).label('user_count'))


        if channelid:
          query_data = query_data.filter(DataEverday.channelid==channelid)
          user_count = user_count.filter(DataMr.channelid==channelid)
        if sp_id:
          query_data = query_data.filter(ChaInfo.spid==sp_id)
          user_count = user_count.filter(ChaInfo.spid==sp_id)

        if order_type:
          if time and order_type == 'time':
            time = time.replace('-', '')
            query_data = query_data.add_column(DataEverday.tj_hour.label('has_index')).filter(DataEverday.tj_date == time).group_by(DataEverday.tj_hour)
            user_count = user_count.add_column(DataMr.regdate.label('has_index')).filter(DataMr.regdate==time).group_by(DataMr.reghour)

          if month and year and order_type == 'month':
            _month_s = '%s%s01' % (year, month)
            _month_e = '%s%s31' % (year, month)

            query_data = query_data.add_column(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(8)')).label('has_index')).\
                        filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).\
                        group_by(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(8)')))

            user_count = user_count.add_column(func.convert(DataMr.regdate, sql.literal_column('CHAR(8)')).label('has_index')).\
                        filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(func.convert(DataMr.regdate, sql.literal_column('CHAR(8)')))

          if year and not month and order_type == 'year':
            _month_s = '%s0101' % year
            _month_e = '%s1231' % year

            query_data = query_data.add_column(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(6)')).label('has_index')).filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).group_by(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(6)')))
            user_count = user_count.add_column(func.convert(DataMr.regdate, sql.literal_column('CHAR(6)')).label('has_index')).\
                        filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(func.convert(DataMr.regdate, sql.literal_column('CHAR(6)')))

        query_data = query_data.all()
        user_count = user_count.all()

        range_date = 24
        if order_type and order_type == 'time':
            range_date = 24

        if month and year and order_type == 'month':
            range_date = calendar.monthrange(int(year), int(month))
            range_date = range_date[1]+1

        if year and not month and order_type == 'year':
          range_date = 13

        t_customize = range(1, range_date)
        t_conversion_rate = range(1, range_date)
        conversion_rate = range(1, range_date)
        into_rate = range(1, range_date)
        arpu = range(1, range_date)
        xAxis = range(1, range_date)
        data_list = {}
        for i in range(0, range_date-1):
            t_customize[i] = 0
            t_conversion_rate[i] = 0
            conversion_rate[i] = 0
            into_rate[i] = 0
            arpu[i] = 0
            xAxis[i] = i + 1

        if query_data:
            for item in query_data:
                _index = 0
                if order_type == 'time':
                  _index = item.has_index
                if order_type == 'month':
                    _year_month = int('%s%s' % (year, month))
                    _index = int(item.has_index) % _year_month
                if order_type == 'year':
                    _index = int(item.has_index) % int(year)
                _index -= 1
                t_customize[_index] = item.mr_all
                item.mo_all = item.mo_all if item.mo_all > 0 else 1
                item.mr_all = item.mr_all if item.mr_all > 0 else 1
                t_conversion_rate[_index] = float(item.mr_all) / float(item.mo_all)
                t_conversion_rate[_index]  = float("%.2f" % t_conversion_rate[_index])
                conversion_rate[_index] = float(item.mr_cp) / float(item.mr_all)
                conversion_rate[_index] = float("%.2f" % conversion_rate[_index])
                into_rate[_index] = float(item.mr_cp) / float(item.mr_all)
                into_rate[_index] = float("%.2f" % into_rate[_index])
                for u in user_count:
                    if u.has_index == item.has_index:
                        arpu[_index] = float(u.user_count) / float(item.mr_all)
                        arpu[_index] = float("%.2f" % arpu[_index])

            data_list['t_customize'] = t_customize
            data_list['t_conversion_rate'] = t_conversion_rate
            data_list['conversion_rate'] = conversion_rate
            data_list['into_rate'] = into_rate
            data_list['arpu'] = arpu
            data_list['range'] = range_date
            data_list['xAxis'] = xAxis
            data_list['title'] = 'TEST DATA'
            return jsonify({'data': data_list, 'ok': True})
        else:
            data_list['t_customize'] = t_customize
            data_list['t_conversion_rate'] = t_conversion_rate
            data_list['conversion_rate'] = conversion_rate
            data_list['into_rate'] = into_rate
            data_list['arpu'] = arpu
            data_list['range'] = range_date
            data_list['xAxis'] = xAxis
            data_list['title'] = 'TEST DATA'
            return jsonify({'data': data_list, 'ok': True})

@operator_view.route("/region/", methods=['GET', 'POST'])
@login_required
def operator_region():
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        today = datetime.datetime.today()
        _month = today.month if today.month >10 else '0%s' % today.month
        _day = today.day if today.day >10 else '0%s' % today.day
        regdate = "%s%s%s" % (today.year, _month, _day)
        query_data = g.session.query(DataEverday.province,func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp')).\
                                    filter(DataEverday.tj_date ==regdate).group_by(DataEverday.province).all()

        user_count = g.session.query(DataMr.province, func.count(distinct(DataMr.mobile)).label('user_count')).filter(DataMr.regdate==regdate).group_by(DataMr.province).all()

        t_customize = range(1, 32)
        t_conversion_rate = range(1, 32)
        conversion_rate = range(1, 32)
        into_rate = range(1, 32)
        arpu = range(1, 32)
        data_list = {}
        for i in range(0, 31):
            t_customize[i] = 0
            t_conversion_rate[i] = 0
            conversion_rate[i] = 0
            into_rate[i] = 0
            arpu[i] = 0

        if query_data:

                for item in query_data:
                    _index = item.province-1
                    t_customize[_index] = item.mr_all
                    item.mo_all = item.mo_all if item.mo_all > 0 else 1
                    item.mr_all = item.mr_all if item.mr_all > 0 else 1
                    t_conversion_rate[_index] = float(item.mr_all) / float(item.mo_all)
                    t_conversion_rate[_index] = float("%.2f" % t_conversion_rate[_index])
                    conversion_rate[_index] = float(item.mr_cp) / float(item.mr_all)
                    conversion_rate[_index] = float("%.2f" % conversion_rate[_index])
                    into_rate[_index] = float(item.mr_cp) / float(item.mr_all)
                    into_rate[_index] = float("%.2f" % into_rate[_index])
                    for u in user_count:
                        if u.province == item.province:
                            arpu[_index] = float(u.user_count) / float(item.mr_all)
                            arpu[_index] = float("%.2f" % arpu[_index])

        data_list['t_customize'] = t_customize
        data_list['t_conversion_rate'] = t_conversion_rate
        data_list['conversion_rate'] = conversion_rate
        data_list['into_rate'] = into_rate
        data_list['arpu'] = arpu
        #data_list['range'] = range_date
        #data_list['xAxis'] = xAxis
        data_list['title'] = 'TEST DATA'
        return render_template('operator_region.html',channels=channels,
                                                        sp_info_list=sp_info_list,
                                                        query_type='time',
                                                        data = json.dumps(data_list),
                                                        random_key = random_key()
                                                        )
    else:
        order_type = req.get('order_type', None)
        time = req.get('time', None)
        month = req.get('month', None)
        year = req.get('year', None)
        channelid = req.get('channel_id', None)
        sp_id = req.get("sp_id", None)
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s%s%s" % (today.year, _month, _day)

        query_data = g.session.query(func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp'), DataEverday.province)

        user_count = g.session.query(DataMr.province, func.count(distinct(DataMr.mobile)).label('user_count'))


        if channelid:
          query_data = query_data.filter(DataEverday.channelid==channelid)
          user_count = user_count.filter(DataMr.channelid==channelid)
        if sp_id:
          query_data = query_data.filter(ChaInfo.spid==sp_id)
          user_count = user_count.filter(ChaInfo.spid==sp_id)

        if order_type:
          if time and order_type == 'time':
            time = time.replace('-', '')
            query_data = query_data.add_column(DataEverday.tj_hour.label('has_index')).filter(DataEverday.tj_date == time).group_by(DataEverday.province)
            user_count = user_count.add_column(DataMr.regdate.label('has_index')).filter(DataMr.regdate==time).group_by(DataMr.province)

          if month and year and order_type == 'month':
            _month_s = '%s%s01' % (year, month)
            _month_e = '%s%s31' % (year, month)

            query_data = query_data.filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).\
                        group_by(DataEverday.province)

            user_count = user_count.filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(DataMr.province)

          if year and not month and order_type == 'year':
            _month_s = '%s0101' % year
            _month_e = '%s1231' % year

            query_data = query_data.filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).group_by(DataEverday.province)
            user_count = user_count.filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(DataMr.province)

        query_data = query_data.all()
        user_count = user_count.all()

        t_customize = range(1, 32)
        t_conversion_rate = range(1, 32)
        conversion_rate = range(1, 32)
        into_rate = range(1, 32)
        arpu = range(1, 32)
        data_list = {}
        for i in range(0, 31):
            t_customize[i] = 0
            t_conversion_rate[i] = 0
            conversion_rate[i] = 0
            into_rate[i] = 0
            arpu[i] = 0


        if query_data:
            for item in query_data:

                _index = item.province - 1
                t_customize[_index] = item.mr_all
                item.mo_all = item.mo_all if item.mo_all > 0 else 1
                item.mr_all = item.mr_all if item.mr_all > 0 else 1
                t_conversion_rate[_index] = float(item.mr_all) / float(item.mo_all)
                t_conversion_rate[_index]  = float("%.2f" % t_conversion_rate[_index])
                conversion_rate[_index] = float(item.mr_cp) / float(item.mr_all)
                conversion_rate[_index] = float("%.2f" % conversion_rate[_index])
                into_rate[_index] = float(item.mr_cp) / float(item.mr_all)
                into_rate[_index] = float("%.2f" % into_rate[_index])
                for u in user_count:
                    if u.province == item.province:
                        arpu[_index] = float(u.user_count) / float(item.mr_all)
                        arpu[_index] = float("%.2f" % arpu[_index])

            data_list['t_customize'] = t_customize
            data_list['t_conversion_rate'] = t_conversion_rate
            data_list['conversion_rate'] = conversion_rate
            data_list['into_rate'] = into_rate
            data_list['arpu'] = arpu
            #data_list['range'] = range_date
            #data_list['xAxis'] = xAxis
            data_list['title'] = 'TEST DATA'

            return jsonify({'data': data_list, 'ok': True})
        else:
            data_list = {}
            data_list['t_customize'] = t_customize
            data_list['t_conversion_rate'] = t_conversion_rate
            data_list['conversion_rate'] = conversion_rate
            data_list['into_rate'] = into_rate
            data_list['arpu'] = arpu
            #data_list['range'] = range_date
            #data_list['xAxis'] = xAxis
            data_list['title'] = 'TEST DATA'
            return jsonify({'data': data_list, 'ok': True})
        return jsonify({'rows': [], 'ok': False})

@operator_view.route("/purpose/", methods=['GET'])
@login_required
def operator_purpose():
    return render_template('operator_purpose.html')
