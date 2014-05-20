# -*- coding: utf-8 -*-

import datetime
import time
import urllib2, urllib
import simplejson
import os
import sys
import md5
reload(sys)
sys.setdefaultencoding("utf-8")

from sqlalchemy import or_, desc, func
from sqlalchemy.orm import subqueryload
from datetime import timedelta
from flask import request, render_template, jsonify, g, Blueprint, Response, redirect, session, url_for
from werkzeug import secure_filename
from OperatorMan.configs import settings
from OperatorMan.views import ok_json, fail_json, check_login, check_administrator



operator_view = Blueprint('operator_view', __name__)

@operator_view.route('/', methods=["GET"])
@check_login(leave=False)
def index():
    if request._is_auth:
        user = request._user
        return redirect(url_for("operator_view.manager_home"))
    else:
        return redirect(url_for('operator_view.login'))

@operator_view.route('/manager/', methods=['GET'])
@check_login(redir='/')
@check_administrator
def manager_home():
    user = request._user
    return render_template("base.html", user_name = user)

@operator_view.route('/login/', methods=['GET', 'POST'])
@check_login(leave=False)
def login():
    if request._is_auth:
        return redirect('/')
    else:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            args = request.form
            username = args.get('username')
            password = args.get('password')
            if not username or not password:
                return u'用户名或密码均不能为空%s' %go_back
            req = rest.Request(settings.P_LOGIN_URI, 'post')
            req.username = username
            req.password = password
            req.ip = request.remote_addr
            resp = req.fetch()
            if resp.ok:
                session_id = resp.data['token']
                session['sid'] = session_id
                response = make_response(redirect('/'))
                session_id = encrypt_token(session_id, request.remote_addr)
                response.set_cookie('token', value=session_id, path='/', domain=settings.COOKIES_DOMAIN, max_age=60*60*20)
                return response
            return u'登陆失败：%s %s' %(resp.data, go_back)
    return 'user login'

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