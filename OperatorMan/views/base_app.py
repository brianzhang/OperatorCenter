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
from OperatorMan.views import ok_json, fail_json, hash_password, write_sys_log
from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync

from OperatorMan.utils import User

base_view = Blueprint('base_view', __name__)



@base_view.route('/', methods=["GET"])
@login_required
def index():
    return render_template("base.html", user = g.user)

@base_view.route('/manager/', methods=['GET'])
@login_required
def manager_home():
    return render_template("base.html", user = g.user)

@base_view.route('/login/', methods=['GET', 'POST'])
def login():
    req = request.args if request.method == 'GET' else request.form
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = req.get('username', None)
        password = req.get('password', None)
        user = g.session.query(SysAdmin).filter(SysAdmin.username==username).\
                filter(SysAdmin.userpwd==hash_password(password)).\
                filter(SysAdmin.is_show==True).first()
        if user:
            login_user(user)
            write_sys_log(1,
                        u'用户登录',
                        u'用户【%s】在【%s】登录了该系统，登录IP为：【%s】'%(user.realname, datetime.datetime.now(), request.remote_addr),
                        user.id)
            return jsonify({'ok': True, 'data': '/'})
        return jsonify({'ok': False, 'username': username, 'reason': u'用户密码错误'})


@base_view.route('/logout/', methods=["GET"])
@login_required
def logout():

    write_sys_log(1,
                    u'退出登录',
                    u'用户【%s】在【%s】退出了系统，注销登录IP为：【%s】' % (g.user.realname, datetime.datetime.now(), request.remote_addr),
                    g.user.id)
    logout_user()
    return redirect('/login/')

@base_view.route('/setpassword/', methods=["POST"])
@login_required
def set_password():
    req = request.args if request.method == 'GET' else request.form
    new_pass = req.get('newpass', None)

    user = g.session.query(SysAdmin).filter(SysAdmin.id==g.user.id).first()
    if user:
        user.userpwd = hash_password(new_pass)
        try:
            g.session.add(user)
            g.session.commit()
            return new_pass

        except Exception, e:
            return jsonify({'ok': False, 'reason': 'SET ERROR.'})
    else:
        return jsonify({'ok': False, 'reason': 'SET ERROR.'})

@base_view.route("/cooperate/operator/page/", methods=['GET'])
@login_required
def sp_info_list():
    admins = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()
    return render_template("sp_info_list.html", admins=admins)

@base_view.route("/cooperate/operator/add/", methods=['POST'])
@base_view.route("/cooperate/operator/edit/<sp_id>/", methods=['POST'])
@login_required
def operator_add(sp_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    if sp_id:
        sp_info = g.session.query(UsrSPInfo).filter(UsrSPInfo.id==sp_id).first()
    else:
        sp_info = UsrSPInfo()
        sp_info.startdate = datetime.datetime.now()

    sp_info.name = req_args.get('name', None)
    sp_info.adminid = req_args.get('adminid', None)
    sp_info.link_name = req_args.get('link_name', None)
    sp_info.link_phone = req_args.get('link_phone', None)
    sp_info.link_qq = req_args.get('link_qq', None)
    sp_info.link_email = req_args.get('link_email', None)
    sp_info.link_address = req_args.get('link_address', None)
    sp_info.enddate = '0000-00-00 00:00:00'
    sp_info.is_show = req_args.get('is_show', False)
    sp_info.content = req_args.get('content', None)
    sp_info.create_time = datetime.datetime.now()

    try:
        g.session.add(sp_info)
        g.session.commit()

        write_sys_log(2,
                    u'设置运营商信息',
                    u'用户【%s】在【%s】设置运营商了信息，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr),
                    g.user.id)

        return jsonify({'ok': True})

    except Exception, e:
        print e

        return jsonify({'errorMsg': 'error'})

@base_view.route("/cooperate/operator/log/", methods=['GET', 'POST'])
@login_required
def operator_log():
    if request.method == 'GET':
        return render_template('usr_sptong_log.html')
    else:
        req_args = request.args if request.method == 'GET' else request.form
        operator_logs_list = g.session.query(UsrSPTongLog).order_by(desc(UsrSPTongLog.id)).all()
        currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(operator_logs_list)

        operator_logs_list = operator_logs_list[start:(numperpage+start)]

        if operator_logs_list:
            operator_logs = []
            for log in operator_logs_list:
                operator_logs.append({'id': log.id,
                                    'channelid': "[%s]%s" % (log.channelid, log.channe_info.cha_name),
                                    'spid': "[%s]%s" % (log.spid, log.sp_info.name),
                                    'urltype': log.urltype,
                                    'mobile': log.mobile,
                                    'spnumber': log.spnumber,
                                    'momsg': log.momsg,
                                    'linkid': log.linkid,
                                    'tongurl': log.tongurl,
                                    'tongdate': log.tongdate,
                                    'is_show': log.is_show,
                                    'create_time': log.create_time
                                    })

            return jsonify({'rows': operator_logs, 'total': total})
        return jsonify({'rows': [], 'total': 0})

@base_view.route("/cooperate/operator/list/", methods=["GET", "POST"])
@login_required
def get_cooperate_operator_list():
    req_args = request.args if request.method == 'GET' else request.form
    operator_list = g.session.query(UsrSPInfo).order_by(desc(UsrSPInfo.id)).all()
    currentpage = int(req_args.get('page', 1))
    numperpage = int(req_args.get('rows', 20))
    start = numperpage * (currentpage - 1)
    total = len(operator_list)
    operator_list = operator_list[start:(numperpage+start)]
    if operator_list:
        operator_data = []
        for sp in operator_list:
            operator_data.append({'id': sp.id,
                                'name': sp.name,
                                'link_name': sp.link_name,
                                'link_phone': sp.link_phone,
                                'link_qq': sp.link_qq,
                                'link_email': sp.link_email,
                                'link_address': sp.link_address,
                                'is_show': sp.is_show,
                                'content': sp.content})

        return jsonify({'rows': operator_data, 'total': total})

@base_view.route("/cooperate/operator/destory/", methods=["GET", "POST"])
@login_required
def set_cooperate_operator_distory():
    req_args = request.args if request.method == 'GET' else request.form
    sp_id = req_args.get('id', None)
    if sp_id:
        sp_info = g.session.query(UsrSPInfo).filter(UsrSPInfo.id==sp_id).first()
        if sp_info:
            sp_info.is_show = False if sp_info.is_show else True
            try:
                g.session.add(sp_info)
                g.session.commit()
                write_sys_log(2,
                        u'合作商合作状态设置',
                        u'用户【%s】在【%s】合作商【%s】合作状态 ，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), sp_info.name, request.remote_addr),
                        g.user.id)
                return jsonify({'success': True})

            except Exception, e:
                return jsonify({'errorMsg': u'操作失败'})
        else:
            return jsonify({'errorMsg': u'合作商信息不存在'})
    else:
        return jsonify({'errorMsg': u'请传递有效的合作商ID信息'})

@base_view.route("/cooperate/channel/list/", methods=["GET", "POST"])
@login_required
def get_cooperate_channel_list():
    req_args = request.args if request.method == 'GET' else request.form

    channel_list = g.session.query(UsrCPInfo).order_by(desc(UsrCPInfo.id)).all()
    currentpage = int(req_args.get('page', 1))
    numperpage = int(req_args.get('rows', 20))
    start = numperpage * (currentpage - 1)
    total = len(channel_list)

    channel_list = channel_list[start:(numperpage+start)]

    if channel_list:
        channel_list_data = []
        for cp in channel_list:
            cp_bank_info = u'收款人：- 开户行：- 帐号：-'
            if cp.bank_info:
                for bank_info in cp.bank_info:
                    cp_bank_info = u'收款人：%s 开户行： %s 帐号： %s' % (bank_info.username, bank_info.bankname, bank_info.bankcard)

            channel_list_data.append({'id': cp.id,
                                'loginname': cp.loginname,
                                'name': cp.name,
                                'bank_info': cp_bank_info,
                                'business': cp.admin_info.realname,
                                'create_time': cp.create_time,
                                'is_show': cp.is_show,
                                'content': cp.content})

        return jsonify({'rows': channel_list_data, 'total': total})

@base_view.route("/cooperate/channel/page/", methods=['GET', 'POST'])
@login_required
def cp_info_list():
    admins = g.session.query(SysAdmin).all()
    return render_template("cp_info_list.html", admins=admins)

@base_view.route("/cooperate/cpinfo/add/", methods=['POST'])
@base_view.route("/cooperate/cpinfo/edit/<cp_id>/", methods=['POST'])
@login_required
def cpinfo_add(cp_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    if cp_id:
        cp_info = g.session.query(UsrCPInfo).filter(UsrCPInfo.id==cp_id).first()
        bank_info = cp_info.bank_info
        if len(bank_info) > 0:
            bank_info = bank_info[0]
        else:
            bank_info = UsrCPBank()
            bank_info.create_time = datetime.datetime.now()
        types = request.args.get('type', None)
        if types:
            if types == 'bank':
                bank_info.bankname = req_args.get('bank_name', None)
                bank_info.username = req_args.get('bank_username', None)
                bank_info.bankcard = req_args.get('bank_card', None)
                bank_info.is_show = req_args.get('bank_is_show', None)
                bank_info.content = req_args.get('bank_content', None)
            if types == 'account':
                cp_info.loginname = req_args.get('txt_loginname', None)
                cp_info.loginpwd = req_args.get('txt_loginpwd', None)
                cp_info.loginpwd = hash_password(cp_info.loginpwd)

    else:
        cp_info = UsrCPInfo()
        bank_info = UsrCPBank()
        cp_info.startdate = datetime.datetime.now()
        cp_info.enddate = '0000-00-00 00:00:00'
        cp_info.create_time = datetime.datetime.now()

        bank_info.create_time = datetime.datetime.now()

        cp_info.loginname = req_args.get('txt_loginname', None)
        cp_info.loginpwd = req_args.get('txt_loginpwd', None)
        cp_info.loginpwd = hash_password(cp_info.loginpwd)

        #bank info module
        bank_info.bankname = req_args.get('bank_name', None)
        bank_info.username = req_args.get('bank_username', None)
        bank_info.bankcard = req_args.get('bank_card', None)
        bank_info.is_show = req_args.get('bank_is_show', None)
        bank_info.content = req_args.get('bank_content', None)

    #cp info module

    cp_info.name = req_args.get('name', None)
    cp_info.adminid = req_args.get('business', None)
    cp_info.link_name = req_args.get('link_name', None)
    cp_info.link_email = req_args.get('link_email', None)
    cp_info.link_phone = req_args.get('link_phone', None)
    cp_info.link_qq = req_args.get('link_qq', None)
    cp_info.link_address = req_args.get('link_address', None)
    cp_info.is_show = req_args.get('is_show', False)
    cp_info.content = req_args.get('content', None)



    try:
        g.session.add(cp_info)
        g.session.commit()

        bank_info.cpid = cp_info.id

        g.session.add(bank_info)
        g.session.commit()

        write_sys_log(2,
                        u'渠道商信息设置',
                        u'用户【%s】在【%s】设置渠道商:【%s】信息，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), cp_info.name, request.remote_addr),
                        g.user.id)

        return jsonify({'ok': True})

    except Exception, e:
        g.session.rollback()
        return jsonify({'errorMsg': 'error'})

#设置合作状态
@base_view.route("/cooperate/cpinfo/partner/", methods=['POST', 'GET'])
@login_required
def cpinfo_partner():
  req_args = request.args if request.method == 'GET' else request.form
  cp_id = req_args.get('id', None)
  if cp_id:
    cp_info = g.session.query(UsrCPInfo).filter(UsrCPInfo.id==cp_id).first()
    if cp_info:
      cp_info.is_show = False if cp_info.is_show else True

      try:
        g.session.add(cp_info)
        g.session.commit()
        write_sys_log(2,
                        u'渠道商合作状态设置',
                        u'用户【%s】在【%s】设置渠道商:【%s】信息，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), cp_info.name, request.remote_addr),
                        g.user.id)
        return jsonify({'ok': True})

      except Exception, e:
        print e
        g.session.rollback()
        return jsonify({'errorMsg': 'error'})

@base_view.route("/cooperate/cpinfo/<cp_id>/", methods=['POST', 'GET'])
@login_required
def cpinfo_get(cp_id=None):
  if cp_id:
      cp_info = g.session.query(UsrCPInfo).filter(UsrSPInfo.id==cp_id).first()
      bank_info = cp_info.bank_info[0]

      render_data = {
        'name': cp_info.name,
        'business': cp_info.adminid,
        'link_name':  cp_info.link_name,
        'link_phone': cp_info.link_phone,
        'link_qq': cp_info.link_qq,
        'link_email': cp_info.link_email,
        'link_address': cp_info.link_address,
        'is_show': cp_info.is_show,
        'content': cp_info.content,
        'txt_loginname': cp_info.loginname,
        'txt_loginpwd': cp_info.loginpwd,
        'bank_name': bank_info.bankname,
        'bank_username': bank_info.username,
        'bank_card': bank_info.bankcard,
        'bank_is_show': bank_info.is_show,
        'bank_content': bank_info.content
      }

      return jsonify(render_data)
  return jsonify({'rows': [], 'total': 0})

@base_view.route("/cooperate/channel/log/", methods=['GET', 'POST'])
@login_required
def channel_log():
    if request.method == 'GET':
        return render_template('usr_cptong_log.html')
    else:
        req_args = request.args if request.method == 'GET' else request.form
        channel_logs_list = g.session.query(UsrCPTongLog).order_by(desc(UsrCPTongLog.id)).all()
        currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(channel_logs_list)

        channel_logs_list = channel_logs_list[start:(numperpage+start)]

        if channel_logs_list:
            channel_logs = []
            for log in channel_logs_list:
                channel_logs.append({'id': log.id,
                                    'channelid': "[%s] %s" % (log.channelid, log.channe_info.cha_name),
                                    'cpid': log.cp_info.name,
                                    'urltype': log.urltype,
                                    'mobile': log.mobile,
                                    'spnumber': log.spnumber,
                                    'momsg': log.momsg,
                                    'linkid': log.linkid,
                                    'tongurl': log.tongurl,
                                    'backmsg': log.backmsg,
                                    'tongdate': log.tongdate,

                                    'create_time': log.create_time
                                    })

            return jsonify({'rows': channel_logs, 'total': total})
        return jsonify({'rows': [], 'total': 0})

@base_view.route("/sys/account/", methods=['GET'])
@login_required
def sys_account():
    roles = g.session.query(SysRole).all()
    return render_template("sys_account.html", roles=roles)

@base_view.route("/sys/account/list/", methods=['GET', 'POST'])
@login_required
def sys_account_list():
    req_args = request.args if request.method == 'GET' else request.form

    admin_list = g.session.query(SysAdmin).all()
    currentpage = int(req_args.get('page', 1))
    numperpage = int(req_args.get('rows', 20))
    start = numperpage * (currentpage - 1)
    total = len(admin_list)

    admin_list = admin_list[start:(numperpage+start)]

    if admin_list:
        admin_list_data = []
        for admin in admin_list:
            admin_list_data.append({'id': admin.id,
                                'username': admin.username,
                                'realname': admin.realname,
                                'role_id': admin.role_id,
                                'phone': admin.phone,
                                'qq': admin.qq,
                                'email': admin.email,
                                'is_show': admin.is_show})

        return jsonify({'rows': admin_list_data, 'total': total})


@base_view.route("/sys/account/add/", methods=['GET', 'POST'])
@base_view.route("/sys/account/edit/<user_id>/", methods=['GET', 'POST'])
@login_required
def sys_account_add(user_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    if user_id:
        admin = g.session.query(SysAdmin).filter(SysAdmin.id==user_id).first()
        write_sys_log(2,
                        u'修改用户信息',
                        u'用户【%s】在【%s】修改了用户信息，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr),
                        g.user.id)
    else:
        write_sys_log(2,
                        u'添加用户',
                        u'用户【%s】在【%s】添加了用户，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr),
                        g.user.id)
        admin = SysAdmin()
    admin.username = req_args.get('username', None)
    admin.userpwd = req_args.get('userpwd', None)
    admin.userpwd = hash_password(admin.userpwd)
    admin.realname = req_args.get('realname', None)
    admin.role_id = req_args.get('role', None)
    admin.phone = req_args.get('phone', None)
    admin.qq = req_args.get('qq', None)
    admin.email = req_args.get('email', None)
    admin.is_show = req_args.get('is_show', False)
    admin.content = req_args.get('content', None)
    admin.create_time = datetime.datetime.now()
    try:
        g.session.add(admin)
        g.session.commit()
        return jsonify({'ok': True})
    except Exception, e:
        return jsonify({'errorMsg': 'error'})
#/sys/account/set/
@base_view.route("/sys/account/set/", methods=['GET', 'POST'])
@login_required
def sys_account_set():
    req_args = request.args if request.method == 'GET' else request.form
    user_id = req_args.get('id', None)
    print user_id
    admin = g.session.query(SysAdmin).filter(SysAdmin.id==user_id).first()
    admin.is_show = False if admin.is_show else True
    try:
        g.session.add(admin)
        g.session.commit()
        write_sys_log(4,
                        u'账号禁用',
                        u'用户【%s】在【%s】禁用账号 【%s】，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), admin.username, request.remote_addr),
                        g.user.id)
        return jsonify({'success': True})
    except Exception, e:
        return jsonify({'errorMsg': 'error'})

@base_view.route("/sys/user/", methods=['GET'])
@login_required
def sys_user():
    roles = g.session.query(SysRole).all()
    user_info = g.session.query(SysAdmin).filter(SysAdmin.id==g.user.id).first()
    return render_template("sys_account_info.html", roles=roles, user=user_info)

@base_view.route("/sys/log/", methods=['GET', 'POST'])
@login_required
def sys_log():
    if request.method == 'GET':
        return render_template('sys_log.html')
    else:
        req_args = request.args if request.method == 'GET' else request.form

        admin_log_list = g.session.query(SysAdminLog).order_by(desc(SysAdminLog.id)).all()
        currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(admin_log_list)

        admin_log_list = admin_log_list[start:(numperpage+start)]

        if admin_log_list:
            admin_log_list_data = []
            for log in admin_log_list:
                admin_log_list_data.append({'id': log.id,
                                    'admin': log.admin.realname,
                                    'op_type': log.op_type,
                                    'op_title': log.op_title,
                                    'op_content': log.op_content,
                                    'create_time': log.create_time})

            return jsonify({'rows': admin_log_list_data, 'total': total})

@base_view.route("/sys/black/", methods=['GET', 'POST'])
@login_required
def sys_balck():
    if request.method == 'GET':
        provinces = g.session.query(PubProvince).all()
        citys = None
        return render_template('pub_black_phone.html', provinces=provinces, citys=None)
    else:
        req_args = request.args if request.method == 'GET' else request.form

        black_list = g.session.query(PubBlackPhone).order_by(desc(PubBlackPhone.id)).all()
        currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(black_list)

        black_list = black_list[start:(numperpage+start)]

        if black_list:
            black_list_data = []
            for black in black_list:
                black_list_data.append({'id': black.id,
                                    'mobile': black.mobile,
                                    'province': black.province_info.province,
                                    'city': black.city_info.city,
                                    'content': black.content,
                                    'create_time': black.create_time})

            return jsonify({'rows': black_list_data, 'total': total})
        else:
            return jsonify({'rows': [], 'total': 0})

@base_view.route("/sys/get/city/", methods=['GET', 'POST'])
@login_required
def sys_get_city():
    req_args = request.args #if request.method == 'GET' else request.form
    province_id = req_args.get('province_id', None)
    citys = g.session.query(PubCity).filter(PubCity.province == province_id).all()

    if citys:
        city_data = []
        for city in citys:
            city_data.append({'id': city.id, 'text': city.city})

        return json.dumps(city_data)

@base_view.route("/sys/black/add/", methods=['GET', 'POST'])
@login_required
def sys_balck_add():
    '''
        add black phone.
    '''
    req_args = request.args if request.method == 'GET' else request.form
    black_phone = PubBlackPhone()
    black_phone.mobile = req_args.get("mobile", None)
    black_phone.province = req_args.get("province", None)
    black_phone.city = req_args.get("city", None)
    black_phone.content = req_args.get("content", None)
    black_phone.create_time = datetime.datetime.now()

    try:
        g.session.add(black_phone)
        g.session.commit()

        write_sys_log(4,
                        u'添加黑名单',
                        u'用户【%s】在【%s】添加手机号【%s】为黑名单，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), black_phone.mobile, request.remote_addr),
                        g.user.id)

        return jsonify({'success': True})

    except Exception, e:

        return jsonify({'errorMsg': 'error'})

def encrypt_token(token, ip):
    '''token加密算法
    生成一个随机的7位前缀，拼接真正的token，拼接访问者ip的hash, 后缀为随机的5位
    '''
    h = uuid.uuid4().hex
    prefix = h[: 7]
    postfix = h[10:15]
    ip_hash = hashlib.md5(ip).hexdigest()
    return prefix + token + ip_hash + postfix

def decrypt_token(token, ip):
    'token解密算法'
    if len(token) == 76:
        token_r = token[7:39]
        iph = token[39:71]
        if iph == hashlib.md5(ip).hexdigest():
            return token_r
