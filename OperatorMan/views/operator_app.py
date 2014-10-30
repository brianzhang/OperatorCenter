# -*- coding: utf-8 -*-

import datetime
import time
import urllib2, urllib
import simplejson as json
import os
import sys
import md5

reload(sys)
sys.setdefaultencoding("utf-8")

from sqlalchemy import or_, desc, func
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
            regdate = "%s%s%s" % (today.year, today.month, today.day)
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
                                    'cp': item.cp_info.name,
                                    'create_time': item.create_time,
                                    'status': item.state,
                                    'is_kill': item.is_kill})

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
        regdate = "%s%s%s" % (today.year, today.month, today.day)
        query_data = g.session.query(DataEverday.tj_hour, func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp')).\
                                    filter(DataEverday.tj_date ==regdate).group_by(DataEverday.tj_hour).all()

        mo_all = range(1, 24)
        mr_all = range(1, 24)
        mr_cp = range(1, 24)
        t_ok = range(1, 24)
        t_mr = range(1, 24)
        t_zh = range(1, 24)
        fc=range(1, 24)
        for i in range(0, 23):
            mo_all[i] = 0
            mr_all[i] = 0
            mr_cp[i] = 0
            t_ok[i] = 0
            t_mr[i] = 0
            t_zh[i] = 0
            fc[i] = 0

        if query_data:
                data_list = {}
                for item in query_data:
                    mo_all[item.tj_hour] = item.mo_all
                    mr_all[item.tj_hour] = item.mr_all
                    mr_cp[item.tj_hour] = item.mr_cp
                    t_ok[item.tj_hour] = (item.mo_all / item.mr_all)
                    t_mr[item.tj_hour] =  (item.mr_all - item.mr_cp)
                    t_zh[item.tj_hour] = 0
                    fc[item.tj_hour] = ((float(item.mr_cp) / float(item.mr_all)) * 100)

        return render_template('operator_exploits.html',channels=channels,
                                                        sp_info_list=sp_info_list,
                                                        query_type='time',
                                                        mo_all = json.dumps(mo_all),
                                                        mr_all = json.dumps(mr_all),
                                                        mr_cp = json.dumps(mr_cp),
                                                        t_ok = json.dumps(t_ok),
                                                        t_mr = json.dumps(t_mr),
                                                        t_zh = json.dumps(t_zh),
                                                        fc = json.dumps(fc),
                                                        regdate=regdate
                                                        )
    else:

        return jsonify({'rows': [], 'total': 0})

@operator_view.route("/region/", methods=['GET', 'POST'])
@login_required
def operator_region():
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':

        channels = g.session.query(ChaInfo).all()
        return render_template('operator_region.html', channels=channels)
    else:
        return jsonify({'rows': [], 'total': 0})

@operator_view.route("/purpose/", methods=['GET'])
@login_required
def operator_purpose():
    return render_template('operator_purpose.html')
