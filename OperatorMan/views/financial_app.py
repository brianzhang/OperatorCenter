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
        #query = g.session.query(UsrSPTongLog)
        query = g.session.query(DataMo, func.count('price').label('total')).group_by(DataMo.regdate).group_by(DataMo.cpid).order_by(desc(DataMo.id))
        #query = query.filter

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
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        return render_template('financial_channel_detail.html', channels=channels, cp_info_list=cp_info_list)
    else:
        return jsonify({'rows': [], 'total': 0})


@financial_view.route("/cooperate/summary/", methods=['GET', 'POST'])
@login_required
def financial_cooperate_summary():
    """
    按照SP所关联的通道在指定条件的时间段里产生的 条数和金额汇总
    """
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        return render_template('financial_cooperate_summary.html', channels=channels, sp_info_list=sp_info_list)
    else:
        return jsonify({'rows': [], 'total': 0})

@financial_view.route("/channel/summary/", methods=['GET', 'POST'])
@login_required
def financial_channel_summary():
    """
    按照CP所关联的通道在指定条件的时间段里产生的 条数和金额汇总
    """
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        return render_template('financial_channel_summary.html', channels=channels, cp_info_list=cp_info_list)
    else:
        return jsonify({'rows': [], 'total': 0})
