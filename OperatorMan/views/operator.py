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
from OperatorCore.models.operator import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UserSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP
from OperatorMan.utils import User

operator_view = Blueprint('operator_view', __name__)



@operator_view.route('/', methods=["GET"])
@login_required
def index():
    return render_template("base.html", user = g.user)

@operator_view.route('/manager/', methods=['GET'])
@login_required
def manager_home():
    return render_template("base.html", user = g.user)

@operator_view.route('/login/', methods=['GET', 'POST'])
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
            return redirect(request.args.get("next") or '/')

        return jsonify({'ok': False, 'username': username, 'pwd': password})


@operator_view.route('/logout/', methods=["GET"])
@login_required
def logout():
    
    write_sys_log(1, 
                    u'退出登录', 
                    u'用户【%s】在【%s】退出了系统，注销登录IP为：【%s】' % (g.user.realname, datetime.datetime.now(), request.remote_addr),
                    g.user.id)
    logout_user()
    return redirect('/login/')


@operator_view.route("/cooperate/operator/page/", methods=['GET'])
@login_required
def operator_list():
    return render_template("operator_list.html")

@operator_view.route("/cooperate/operator/log/", methods=['GET'])
@login_required
def operator_log():
    return 'operator_log'

@operator_view.route("/cooperate/operator/list/", methods=["GET", "POST"])
@login_required
def get_cooperate_operator_list():
    req_args = request.args if request.method == 'GET' else request.form
    print req_args
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
                                'link_address': sp.link_address, 
                                'is_show': sp.is_show,
                                'content': sp.content})

        return jsonify({'rows': operator_data, 'total': total})

@operator_view.route("/cooperate/channel/list/", methods=["GET", "POST"])
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
            bank_info = g.session.query(UsrCPBank).filter(UsrCPBank.cpid == cp.id).first()
            cp_bank_info = u'收款人：- 开户行：- 帐号：-'
            if bank_info:
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

@operator_view.route("/cooperate/channel/page/", methods=['GET'])
@login_required
def channel_page():
    return render_template("channel_list.html")

@operator_view.route("/cooperate/channel/log/", methods=['GET'])
@login_required
def channel_log():
    return 'channel_log'

@operator_view.route("/operator/status/", methods=['GET'])
@login_required
def operator_status():
    return 'operator_status'

@operator_view.route("/operator/demand/", methods=['GET'])
@login_required
def operator_demand():
    return 'operator_demand'

@operator_view.route("/operator/exploits/", methods=['GET'])
@login_required
def operator_exploits():
    return 'operator_exploits'

@operator_view.route("/operator/region/", methods=['GET'])
@login_required
def operator_region():
    return 'operator_region'

@operator_view.route("/operator/purpose/", methods=['GET'])
@login_required
def operator_purpose():
    return 'operator_purpose'

@operator_view.route("/channel/list/", methods=['GET'])
@login_required
def channel_list():
    return 'channel_list'

@operator_view.route("/channel/settings/", methods=['GET'])
@login_required
def channel_settings():
    return 'channel_settings'

@operator_view.route("/channel/sync/", methods=['GET'])
@login_required
def channel_sync():
    return 'channel_sync'

@operator_view.route("/channel/cover/", methods=['GET'])
@login_required
def channel_cover():
    return 'channel_cover'

@operator_view.route("/financial/cooperate/detail/", methods=['GET'])
@login_required
def financial_cooperate_detail():
    return 'financial_cooperate_detail'

@operator_view.route("/financial/channel/detail/", methods=['GET'])
@login_required
def financial_channel_detail():
    return 'financial_channel_detail'


@operator_view.route("/financial/cooperate/summary/", methods=['GET'])
@login_required
def financial_cooperate_summary():
    return 'financial_cooperate_summary'

@operator_view.route("/financial/channel/summary/", methods=['GET'])
@login_required
def financial_channel_summary():
    return 'financial_channel_summary'

@operator_view.route("/sys/account/", methods=['GET'])
@login_required
def sys_account():
    roles = g.session.query(SysRole).all()
    return render_template("sys_account.html", roles=roles)

@operator_view.route("/sys/account/list/", methods=['GET', 'POST'])
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


@operator_view.route("/sys/account/add/", methods=['GET', 'POST'])
@operator_view.route("/sys/account/edit/<user_id>/", methods=['GET', 'POST'])
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
@operator_view.route("/sys/account/set/", methods=['GET', 'POST'])
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

@operator_view.route("/sys/user/", methods=['GET'])
@login_required
def sys_user():
    roles = g.session.query(SysRole).all()
    user_info = g.session.query(SysAdmin).filter(SysAdmin.id==g.user.id).first()
    return render_template("sys_account_info.html", roles=roles, user=user_info)

@operator_view.route("/sys/log/", methods=['GET', 'POST'])
@login_required
def sys_log():
    if request.method == 'GET':
        return render_template('sys_log.html')
    else:
        req_args = request.args if request.method == 'GET' else request.form

        admin_log_list = g.session.query(SysAdminLog).all()
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

@operator_view.route("/sys/balck/", methods=['GET', 'POST'])
@login_required
def sys_balck():
    if request.method == 'GET':
        provinces = g.session.query(PubProvince).all()
        citys = None
        return render_template('pub_black_phone.html', provinces=provinces, citys=None)
    else:
        req_args = request.args if request.method == 'GET' else request.form

        black_list = g.session.query(PubBlackPhone).all()
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
    
@operator_view.route("/sys/get/city/", methods=['GET', 'POST'])
@login_required
def sys_get_city():
    req_args = request.args if request.method == 'GET' else request.form
    province_id = req_args.get('province_id', None)
    citys = g.session.query(PubCity).filter(PubCity.province == province_id).all()

    if citys:
        city_data = []
        for city in citys:
            city_data.append({'id': city.id, 'text': city.city})

        return jsonify({'data': city_data})

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
