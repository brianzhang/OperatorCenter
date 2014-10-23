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
    状态报告
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
    点播上行
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
        return render_template('operator_exploits.html',channels=channels,
                                                        sp_info_list=sp_info_list,
                                                        query_type='time')
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
