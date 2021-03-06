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

from sqlalchemy import or_, desc, func, distinct, CHAR, sql
from sqlalchemy.orm import subqueryload

from datetime import timedelta
from flask import request, render_template, jsonify, g, Blueprint, Response, redirect, session, url_for, send_from_directory
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
import flask.ext.wtf as wtf

from werkzeug import secure_filename
from OperatorMan.configs import settings
from OperatorMan.views import ok_json, fail_json, hash_password, write_sys_log, random_key, execl_import
from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync

from OperatorMan.utils import User

financial_view = Blueprint('financial_view', __name__, url_prefix='/financial')

@financial_view.route("/channel/explort/", methods=['GET', 'POST'])
@login_required
def financial_channel_explort():
    req = request.args if request.method == 'GET' else request.form
    print '-------------------------------------'
    today = datetime.datetime.today()
    _month = today.month if today.month > 10 else '0%s' % today.month
    _day = today.day if today.day > 10 else '0%s' % today.day
    regdate = "%s-%s-%s" % (today.year, _month, _day)
    tab_name = "%s%s%s" % (today.year, _month, _day)
    start_time = req.get('start_time', None)
    end_time = req.get('end_time', None)
    channel = req.get('channel', None)
    explort_data = "%s-%s" % (start_time, end_time)
    cp = req.get('cp', None)

    query = g.session.query(AccountCP).order_by(desc(AccountCP.js_date))
    total_query  = g.session.query(func.sum(AccountCP.count).label('all_count'), func.sum(AccountCP.totalprice).label('totalprice_count'))
    footers = []

    #query = query.filter
    if start_time:
      start_time += ' 00:00:00'
      query = query.filter(AccountCP.create_time >= start_time)
      total_query = total_query.filter(AccountCP.create_time >= start_time)
    if end_time:
      end_time += ' 23:59:59'
      query = query.filter(AccountCP.create_time <= end_time)
      total_query = total_query.filter(AccountCP.create_time <= end_time)
    if channel:
      query = query.filter(AccountCP.channelid == channel)
      total_query = total_query.filter(AccountCP.channelid == channel)
    if cp:
      query = query.filter(AccountCP.cpid == cp)
      total_query = total_query.filter(AccountCP.cpid == cp)

    sp_operate_list = query.all()
    total_query = total_query.all()

    sp_name = u"渠道商："
    sp_operate_data = []
    if sp_operate_list:        
        sp_name = sp_name + " "+ sp_operate_list[0].cp_info.name
        for item in sp_operate_list:
            if item:
                
                sp_operate_data.append({
                                    'id': item.id,
                                    'regdate': item.js_date,
                                    'spname': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
                                    'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                    'price': item.price,
                                    'costprice': item.fcprice,
                                    'count': item.count,
                                    'total': item.totalprice,
                                    'status': item.js_state,
                                    'charges_total': (item.price * item.count)
                                    })

    file_name =  execl_import(data=sp_operate_data, 
                                      title=u"渠道商结算对账单",
                                      sp_name=sp_name, 
                                      tab_name=tab_name, 
                                      account_name= '', 
                                      bank_name='', 
                                      account='',
                                      summerize_data=explort_data)
    print file_name
    return send_from_directory(settings.FILE_PATH, file_name, as_attachment=True)


@financial_view.route("/cooperate/explort/", methods=['GET', 'POST'])
@login_required
def financial_cooperate_explort():
    req = request.args if request.method == 'GET' else request.form
    today = datetime.datetime.today()
    _month = today.month if today.month > 10 else '0%s' % today.month
    _day = today.day if today.day > 10 else '0%s' % today.day
    regdate = "%s-%s-%s" % (today.year, _month, _day)
    tab_name = "%s%s%s" % (today.year, _month, _day)
    start_time = req.get('start_time', None)
    end_time = req.get('end_time', None)
    explort_data = "%s-%s" % (start_time, end_time)
    channel = req.get('channel', None)
    sp = req.get('sp', None)

    

    query = g.session.query(AccountSP).order_by(desc(AccountSP.js_date))
    total_query  = g.session.query(func.sum(AccountSP.count).label('all_count'), func.sum(AccountSP.totalprice).label('totalprice_count'))
    footers = []
    #query = query.filter
    if start_time:
      start_time += ' 00:00:00'
      query = query.filter(AccountSP.create_time >= start_time)
      total_query = total_query.filter(AccountSP.create_time >= start_time)
    if end_time:
      end_time += ' 23:59:59'
      query = query.filter(AccountSP.create_time <= end_time)
      total_query = total_query.filter(AccountSP.create_time <= end_time)
    if channel:
      query = query.filter(AccountSP.channelid == channel)
      total_query = total_query.filter(AccountSP.channelid == channel)
    if sp:
      query = query.filter(AccountSP.spid == sp)
      total_query = total_query.filter(AccountSP.spid == sp)
    sp_operate_list = query.all()
    total_query = total_query.all()

    sp_name = u"合作方："
    sp_operate_data = []
    if sp_operate_list:        
        sp_name = sp_name + " "+ sp_operate_list[0].sp_info.name
        for item in sp_operate_list:
            if item:
                
                sp_operate_data.append({
                                    'id': item.id,
                                    'regdate': item.js_date,
                                    'spname': "[%s]%s" % (item.sp_info.id, item.sp_info.name),
                                    'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                    'price': item.price,
                                    'costprice': item.costprice,
                                    'count': item.count,
                                    'total': item.totalprice,
                                    'status': item.js_state,
                                    'charges_total': (item.price * item.count)
                                    })

    file_name =  execl_import(data=sp_operate_data, 
                                      title=u"合作方结算对账单",
                                      sp_name=sp_name, 
                                      tab_name=tab_name, 
                                      account_name= '', 
                                      bank_name='', 
                                      account='',
                                      summerize_data=explort_data)
    return send_from_directory(settings.FILE_PATH, file_name, as_attachment=True)

@financial_view.route("/cooperate/detail/", methods=['GET', 'POST'])
@login_required
def financial_cooperate_detail():
    #按天查询SP所关联的通道产生的条数和金额 合作方明细
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        return render_template('financial_cooperate_detail.html', channels=channels, sp_info_list=sp_info_list, random_key=random_key(), regdate=regdate, cp_info_list=cp_info_list)
    else:
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        sp = req.get('sp', None)

        

        query = g.session.query(AccountSP).order_by(desc(AccountSP.js_date))
        total_query  = g.session.query(func.sum(AccountSP.count).label('all_count'), func.sum(AccountSP.totalprice).label('totalprice_count'))
        footers = []
        #query = query.filter
        if start_time:
          start_time += ' 00:00:00'
          query = query.filter(AccountSP.create_time >= start_time)
          total_query = total_query.filter(AccountSP.create_time >= start_time)
        if end_time:
          end_time += ' 23:59:59'
          query = query.filter(AccountSP.create_time <= end_time)
          total_query = total_query.filter(AccountSP.create_time <= end_time)
        if channel:
          query = query.filter(AccountSP.channelid == channel)
          total_query = total_query.filter(AccountSP.channelid == channel)
        if sp:
          query = query.filter(AccountSP.spid == sp)
          total_query = total_query.filter(AccountSP.spid == sp)
        sp_operate_list = query.all()
        total_query = total_query.all()
        total = len(sp_operate_list)
        
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)        

        sp_operate_list = sp_operate_list[start:(numperpage+start)]
        if total_query:
            _all_count  = total_query[0].all_count if total_query[0].all_count else 0
            _totalprice_count = total_query[0].totalprice_count if total_query[0].totalprice_count else 0
            footers.append({
                'id': u'汇总',
                'count':  _all_count,
                'total': '%.2f' % _totalprice_count,
                'status': 'footer'
            })
        if sp_operate_list:
            sp_operate_data = []
            for item in sp_operate_list:
                if item:
                    sp_operate_data.append({
                                        'id': item.id,
                                        'regdate': item.js_date,
                                        'spname': "[%s]%s" % (item.sp_info.id, item.sp_info.name),
                                        'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                        'price': item.price,
                                        'costprice': item.costprice,
                                        'count': item.count,
                                        'total': item.totalprice,
                                        'status': item.js_state,
                                        'charges_total': (item.price * item.count)
                                        })

            return jsonify({'rows': sp_operate_data, 'total': total, 'footer': footers})

        return jsonify({'rows': [], 'total': 0, 'footer': {'id': u'汇总', 'count': 0, 'total': 0, 'status': 'footer'}})


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
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)
        return render_template('financial_channel_detail.html', channels=channels, cp_info_list=cp_info_list, regdate=regdate)
    else:
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        cp = req.get('cp', None)

        query = g.session.query(AccountCP).order_by(desc(AccountCP.js_date))
        total_query  = g.session.query(func.sum(AccountCP.count).label('all_count'), func.sum(AccountCP.totalprice).label('totalprice_count'))
        footers = []

        #query = query.filter
        if start_time:
          start_time += ' 00:00:00'
          query = query.filter(AccountCP.create_time >= start_time)
          total_query = total_query.filter(AccountCP.create_time >= start_time)
        if end_time:
          end_time += ' 23:59:59'
          query = query.filter(AccountCP.create_time <= end_time)
          total_query = total_query.filter(AccountCP.create_time <= end_time)
        if channel:
          query = query.filter(AccountCP.channelid == channel)
          total_query = total_query.filter(AccountCP.channelid == channel)
        if cp:
          query = query.filter(AccountCP.cpid == cp)
          total_query = total_query.filter(AccountCP.cpid == cp)

        sp_operate_list = query.all()
        total_query = total_query.all()

        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(sp_operate_list)
        sp_operate_list = sp_operate_list[start:(numperpage+start)]
        if total_query:
            footers.append({
                'regdate': u'总计',
                'count':  total_query[0].all_count,
                'total': '%.2f' % total_query[0].totalprice_count,
                'status': 'footer'
            })

        if sp_operate_list:
            sp_operate_data = []
            for item in sp_operate_list:
                if item:
                    sp_operate_data.append({
                                        'id': item.id,
                                        'regdate': item.js_date,
                                        'cpname': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
                                        'channel': "[%s]%s" % (item.channe_info.id, item.channe_info.cha_name),
                                        'price': item.price,
                                        'fcprice': item.fcprice,
                                        'count': item.count,
                                        'total': item.totalprice,
                                        'status': item.js_state,
                                        'charges_total': float('%.2f' % (item.count*item.price))
                                        })

            return jsonify({'rows': sp_operate_data, 'total': total, 'footer': footers})

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
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        return render_template('financial_cooperate_summary.html', channels=channels, sp_info_list=sp_info_list, random_key=random_key(), regdate=regdate)
    else:
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        sp = req.get('sp', None)

        query = g.session.query(AccountSP, func.sum(AccountSP.count).label('count'), func.sum(AccountSP.totalprice).label('totalprice')).group_by(AccountSP.js_date).group_by(AccountSP.spid)
        
        if start_time:
          start_time += ' 00:00:00'
          query = query.filter(AccountSP.create_time >= start_time)
        if end_time:
          end_time += ' 23:59:59'
          query = query.filter(AccountSP.create_time <= end_time)
        if channel:
          query = query.filter(AccountSP.channelid == channel)

        if sp:
          query = query.filter(AccountSP.spid == sp)


        summarize_lsit = query.order_by(desc(AccountSP.js_date)).all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(summarize_lsit)
        summarize_lsit = summarize_lsit[start:(numperpage+start)]
        if summarize_lsit:
          render_data = []
          for item in summarize_lsit:
            count = item.count
            totalprice = item.totalprice
            item = item[0]
            render_data.append({
              'sp': "[%s]%s" % (item.sp_info.id, item.sp_info.name),
              'count': count,
              'total': float('%.2f' % totalprice),
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

        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        return render_template('financial_channel_summary.html', channels=channels, cp_info_list=cp_info_list, random_key=random_key(), regdate=regdate)
    else:
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)

        start_time = req.get('start_time', None)
        end_time = req.get('end_time', None)
        channel = req.get('channel', None)
        cp = req.get('cp', None)

        query = g.session.query(AccountCP, func.sum(AccountCP.count).label('count'), func.sum(AccountCP.totalprice).label('totalprice')).group_by(AccountCP.js_date).group_by(AccountCP.cpid)
        
        if start_time:
          start_time += ' 00:00:00'
          query = query.filter(AccountCP.create_time >= start_time)
        if end_time:
          end_time += ' 23:59:59'
          query = query.filter(AccountCP.create_time <= end_time)
        if channel:
          query = query.filter(AccountCP.channelid == channel)

        if cp:
          query = query.filter(AccountCP.cpid == cp)


        summarize_lsit = query.order_by(desc(AccountCP.js_date)).all()
        currentpage = int(req.get('page', 1))
        numperpage = int(req.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(summarize_lsit)
        summarize_lsit = summarize_lsit[start:(numperpage+start)]
        if summarize_lsit:
          render_data = []
          for item in summarize_lsit:
            count = item.count
            totalprice = item.totalprice
            item = item[0]
            render_data.append({
              'cp': "[%s]%s" % (item.cp_info.id, item.cp_info.name),
              'count': count,
              'total': float('%.2f' % totalprice),
              'date_time': item.create_time
            })
          return jsonify({'rows': render_data, 'total': total})
        else:
          return jsonify({'rows': [], 'total': 0})

#/channel/billing/
#cooperate
@financial_view.route("/channel/billing/", methods=['POST'])
@login_required
def financial_channel_billing():
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'POST':
        c_id = req.get('id', None)
        c_types = req.get('types', None)
        values = req.get('values', None)
        try:
            account = g.session.query(AccountCP).filter(AccountCP.id==c_id).first()
            if account:
                if c_types == '1':
                    account.fcprice = values
                elif c_types == '2':
                    account.count = values
                account.totalprice = int(account.count) * float(account.fcprice)
                g.session.add(account)
                g.session.commit()
                return jsonify({'errorMsg': False})
            else:
                return jsonify({'errorMsg': u'结算不存在！'})    
        except Exception, e:
            return jsonify({'errorMsg': u'设置失败！'})    
        return jsonify({'errorMsg': False})

@financial_view.route("/cooperate/billing/", methods=['POST'])
@login_required
def financial_cooperate_billing():
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'POST':
        c_id = req.get('id', None)
        c_types = req.get('types', None)
        values = req.get('values', None)
        try:
            account = g.session.query(AccountSP).filter(AccountSP.id==c_id).first()
            if account:
                if c_types == '1':
                    account.costprice = values
                elif c_types == '2':
                    account.count = values
                account.totalprice = int(account.count) * float(account.costprice)
                g.session.add(account)
                g.session.commit()
                return jsonify({'errorMsg': False})
            else:
                return jsonify({'errorMsg': u'结算不存在！'})    
        except Exception, e:
            return jsonify({'errorMsg': u'设置失败！'})    
        return jsonify({'errorMsg': False})

@financial_view.route("/cooperate/add/", methods=['POST'])
@login_required
def financial_cooperate_add():
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'POST':
        sp_id = req.get('sp_info', None)
        channel_id = req.get('channel_info', None)
        values = req.get('count', None)
        cp_id = req.get('cp_info', None)
        try:
            today = datetime.datetime.today()
            _month = today.month if today.month > 10 else '0%s' % today.month
            _day = today.day if today.day > 10 else '0%s' % today.day
            regdate = "%s%s%s" % (today.year, _month, _day)
            account = AccountSP()
            channel = g.session.query(ChaInfo).filter(ChaInfo.id==channel_id).first()
            cp_channel = g.session.query(UsrChannel).filter(UsrChannel.channelid==channel_id).filter(UsrChannel.cpid==cp_id).first()
            account.spid = sp_id
            account.channelid = channel_id
            account.count = values
            account.price =channel.price
            account.costprice = channel.costprice
            account.totalprice = int(account.count) * float(account.costprice)
            account.js_state = True
            account.js_date = regdate
            account.create_time = datetime.datetime.now()

            account_cp = AccountCP()
            account_cp.cpid = cp_id
            account_cp.channelid = channel_id
            account_cp.price = channel.price
            account_cp.fcprice = cp_channel.fcprice
            account_cp. count= int(values) - int(int(values)-int(cp_channel.bl)) * float(cp_channel.bl/100.0)
            account_cp.totalprice = int(account_cp.count) * float(account_cp.fcprice)
            account_cp.js_state = True
            account_cp.js_date = regdate
            account_cp.create_time = datetime.datetime.now()

            g.session.add(account)
            g.session.add(account_cp)
            g.session.commit()
            return jsonify({'errorMsg': False})
        except Exception, e:
            return jsonify({'errorMsg': u'设置失败！'})    
        return jsonify({'errorMsg': False})
