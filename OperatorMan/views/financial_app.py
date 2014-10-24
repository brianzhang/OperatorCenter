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

financial_view = Blueprint('financial_view', __name__, url_prefix='/financial')


@financial_view.route("/cooperate/detail/", methods=['GET', 'POST'])
@login_required
def financial_cooperate_detail():
    #按天查询SP所关联的通道产生的条数和金额
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        return render_template('financial_cooperate_detail.html', channels=channels, sp_info_list=sp_info_list, random_key=random_key())
    else:

        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        sp = req.get('sp', None)

        query = g.session.query(DataMo, func.count('price').label('total')).group_by(DataMo.regdate).group_by(DataMo.cpid).order_by(desc(DataMo.id))
        #query = query.filter
        if start_time:
          start_time += '00:00:00'
          query = query.filter(DataMo.create_time >= start_time)
        if end_time:
          end_time += '00:00:00'
          query = query.filter(DataMo.create_time <= start_time)
        if channel:
          query = query.filter(DataMo.channelid == channel)

        if sp:
          query = query.filter(DataMo.channe_info.sp_info.id == sp)

        sp_operate_list = query.all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(sp_operate_list)
        sp_operate_list = sp_operate_list[start:(numperpage+start)]

        if sp_operate_list:
            sp_operate_data = []
            for item in sp_operate_list:
                total = item.total
                item = item[0]
                if item:
                    sp_operate_data.append({'regdate': item.regdate,
                                        'spname': "[%s]%s" % (item.channe_info.sp_info.id, item.channe_info.sp_info.name),
                                        'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                        'price': item.channe_info.price,
                                        'costprice': item.channe_info.costprice,
                                        'count': total,
                                        'total': (item.channe_info.price * total)
                                        })

            return jsonify({'rows': sp_operate_data, 'total': total})

        return jsonify({'rows': [], 'total': 0})


@financial_view.route("/channel/detail/", methods=['GET', 'POST'])
@login_required
def financial_channel_detail():
    """
      按天查询CP所关联的通道产生的条数和金额汇总 条件以某个时间段

    """
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        return render_template('financial_channel_detail.html', channels=channels, cp_info_list=cp_info_list)
    else:
        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        cp = req.get('cp', None)
        query = g.session.query(DataMr, func.count('price').label('total')).group_by(DataMr.regdate).group_by(DataMr.cpid).order_by(desc(DataMr.id))
        #query = query.filter
        if start_time:
          start_time += '00:00:00'
          query = query.filter(DataMr.create_time >= start_time)
        if end_time:
          end_time += '00:00:00'
          query = query.filter(DataMr.create_time <= start_time)
        if channel:
          query = query.filter(DataMr.channelid == channel)

        if cp:
          query = query.filter(DataMr.cpid == cp)

        sp_operate_list = query.all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(sp_operate_list)
        sp_operate_list = sp_operate_list[start:(numperpage+start)]

        if sp_operate_list:
            sp_operate_data = []
            for item in sp_operate_list:
                total = item.total
                item = item[0]
                if item:
                    sp_operate_data.append({'regdate': item.regdate,
                                        'cpname': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
                                        'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                        'price': item.channe_info.price,
                                        'costprice': item.channe_info.costprice,
                                        'count': total,
                                        'total': (item.channe_info.price * total)
                                        })

            return jsonify({'rows': sp_operate_data, 'total': total})

        return jsonify({'rows': [], 'total': 0})


@financial_view.route("/cooperate/summary/", methods=['GET', 'POST'])
@login_required
def financial_cooperate_summary():
    """
    按照SP所关联的通道在指定条件的时间段里产生的 条数和金额汇总
    """
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        return render_template('financial_cooperate_summary.html', channels=channels, sp_info_list=sp_info_list, random_key=random_key())
    else:
        query = g.session.query(AccountSP)
        summarize_lsit = query.all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(summarize_lsit)
        summarize_lsit = summarize_lsit[start:(numperpage+start)]
        if summarize_lsit:
          render_data = []
          for item in summarize_lsit:
            render_data.append({
              'sp': "[%s]%s" % (item.sp_info.id, item.sp_info.name),
              'channel_name': '[%s]%s' % (item.channe_info.id, item.channe_info.cha_name),
              'costprice': item.costprice,
              'count': item.count,
              'price': item.price,
              'total': item.totalprice,
              'date_time': item.create_time
            })
          return jsonify({'rows': render_data, 'total': total})
        else:
          return jsonify({'rows': [], 'total': 0})

@financial_view.route("/channel/summary/", methods=['GET', 'POST'])
@login_required
def financial_channel_summary():
    """
    按照CP所关联的通道在指定条件的时间段里产生的 条数和金额汇总
    """
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()

        return render_template('financial_channel_summary.html', channels=channels, cp_info_list=cp_info_list, random_key=random_key())
    else:
        query = g.session.query(AccountCP)
        summarize_lsit = query.all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(summarize_lsit)
        summarize_lsit = summarize_lsit[start:(numperpage+start)]
        if summarize_lsit:
          render_data = []
          for item in summarize_lsit:
            render_data.append({
              'cp': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
              'channel_name': '[%s]%s' % (item.channe_info.id, item.channe_info.cha_name),
              'costprice': item.fcprice,
              'count': item.count,
              'price': item.price,
              'total': item.totalprice,
              'date_time': item.create_time
            })
          return jsonify({'rows': render_data, 'total': total})
        else:
          return jsonify({'rows': [], 'total': 0})
