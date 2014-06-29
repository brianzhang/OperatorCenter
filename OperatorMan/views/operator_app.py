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

operator_view = Blueprint('operator_view', __name__, url_prefix='/operator')


@operator_view.route("/status/", methods=['GET', 'POST'])
@login_required
def operator_status():
    
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':
        channels = g.session.query(ChaInfo).filter(ChaInfo.is_show==True).all()
        sp_info_list = g.session.query(UsrSPInfo).filter(UsrSPInfo.is_show==True).all()
        provinces = g.session.query(PubProvince).all()
        users = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()

        return  render_template('operator_status.html', channels=channels, 
                                                        sp_info_list=sp_info_list,
                                                        provinces=provinces,
                                                        users=users)
    else:
        return jsonify({'rows': [], 'total': 0})

@operator_view.route("/demand/", methods=['GET', 'POST'])
@login_required
def operator_demand():
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':
        channels = g.session.query(ChaInfo).filter(ChaInfo.is_show==True).all()
        sp_info_list = g.session.query(UsrSPInfo).filter(UsrSPInfo.is_show==True).all()
        provinces = g.session.query(PubProvince).all()
        users = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()

        return  render_template('operator_demand.html', channels=channels, 
                                                        sp_info_list=sp_info_list,
                                                        provinces=provinces,
                                                        users=users)
    else:
        return jsonify({'rows': [], 'total': 0})

@operator_view.route("/exploits/", methods=['GET', 'POST'])
@login_required
def operator_exploits():
    req = request.args if request.method == 'GET' else request.form

    if request.method == 'GET':
        channels = g.session.query(ChaInfo).filter(ChaInfo.is_show==True).all()
        sp_info_list = g.session.query(UsrSPInfo).filter(UsrSPInfo.is_show==True).all()
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

        channels = g.session.query(ChaInfo).filter(ChaInfo.is_show==True).all()
        return render_template('operator_region.html', channels=channels)
    else:
        return jsonify({'rows': [], 'total': 0})

@operator_view.route("/purpose/", methods=['GET'])
@login_required
def operator_purpose():
    return render_template('operator_purpose.html')