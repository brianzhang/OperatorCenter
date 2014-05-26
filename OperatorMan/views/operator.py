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
from OperatorMan.views import ok_json, fail_json, hash_password
from OperatorCore.models.operator import SysAdmin, SysAdminLog, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
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

@operator_view.route("/get/data/", methods=['GET'])
def get_data():
    return jsonify({"total":28,"rows":[
    {"productid":"FI-SW-01","productname":"Koi","unitcost":10.00,"status":"P","listprice":36.50,"attr1":"Large","itemid":"EST-1"},
    {"productid":"K9-DL-01","productname":"Dalmation","unitcost":12.00,"status":"P","listprice":18.50,"attr1":"Spotted Adult Female","itemid":"EST-10"},
    {"productid":"RP-SN-01","productname":"Rattlesnake","unitcost":12.00,"status":"P","listprice":38.50,"attr1":"Venomless","itemid":"EST-11"},
    {"productid":"RP-SN-01","productname":"Rattlesnake","unitcost":12.00,"status":"P","listprice":26.50,"attr1":"Rattleless","itemid":"EST-12"},
    {"productid":"RP-LI-02","productname":"Iguana","unitcost":12.00,"status":"P","listprice":35.50,"attr1":"Green Adult","itemid":"EST-13"},
    {"productid":"FL-DSH-01","productname":"Manx","unitcost":12.00,"status":"P","listprice":158.50,"attr1":"Tailless","itemid":"EST-14"},
    {"productid":"FL-DSH-01","productname":"Manx","unitcost":12.00,"status":"P","listprice":83.50,"attr1":"With tail","itemid":"EST-15"},
    {"productid":"FL-DLH-02","productname":"Persian","unitcost":12.00,"status":"P","listprice":23.50,"attr1":"Adult Female","itemid":"EST-16"},
    {"productid":"FL-DLH-02","productname":"Persian","unitcost":12.00,"status":"P","listprice":89.50,"attr1":"Adult Male","itemid":"EST-17"},
    {"productid":"AV-CB-01","productname":"Amazon Parrot","unitcost":92.00,"status":"P","listprice":63.50,"attr1":"Adult Male","itemid":"EST-18"}
    ]})

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
            return redirect(request.args.get("next") or '/')

        return jsonify({'ok': False, 'username': username, 'pwd': password})


@operator_view.route('/logout/', methods=["GET"])
@login_required
def logout():
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
    operator_list = g.session.query(UsrSPInfo).all()
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

    channel_list = g.session.query(UsrCPInfo).all()
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
                                'business': cp.adminid,
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
    return 'sys_account'

@operator_view.route("/sys/user/", methods=['GET'])
@login_required
def sys_user():
    return 'sys_user'

@operator_view.route("/sys/log/", methods=['GET'])
@login_required
def sys_log():
    return 'sys_log'

@operator_view.route("/sys/balck/", methods=['GET'])
@login_required
def sys_balck():
    return 'sys_balck'

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
