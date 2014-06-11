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

@operator_view.route('/setpassword/', methods=["POST"])
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

@operator_view.route("/cooperate/operator/page/", methods=['GET'])
@login_required
def sp_info_list():
    admins = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()
    return render_template("sp_info_list.html", admins=admins)

@operator_view.route("/cooperate/operator/add/", methods=['POST'])
@operator_view.route("/cooperate/operator/edit/<sp_id>/", methods=['POST'])
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
        return jsonify({'errorMsg': 'error'})

@operator_view.route("/cooperate/operator/log/", methods=['GET', 'POST'])
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
                                    'channelid': log.channelid, 
                                    'spid': log.spid,
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

@operator_view.route("/cooperate/operator/list/", methods=["GET", "POST"])
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
                                'link_address': sp.link_address, 
                                'is_show': sp.is_show,
                                'content': sp.content})

        return jsonify({'rows': operator_data, 'total': total})

@operator_view.route("/cooperate/operator/destory/", methods=["GET", "POST"])
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

@operator_view.route("/cooperate/channel/page/", methods=['GET', 'POST'])
@login_required
def cp_info_list():
    admins = g.session.query(SysAdmin).all()
    return render_template("cp_info_list.html", admins=admins)

@operator_view.route("/cooperate/cpinfo/add/", methods=['POST'])
@operator_view.route("/cooperate/cpinfo/edit/<cp_id>/", methods=['POST'])
@login_required
def cpinfo_add(cp_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    if cp_id:
        cp_info = g.session.query(UsrCPInfo).filter(UsrSPInfo.id==cp_id).first()
        bank_info = cp_info.bank_info
        if len(bank_info) > 0:
            bank_info = bank_info[0]
        else:
            bank_info = UsrCPBank()
            bank_info.create_time = datetime.datetime.now()
    else:
        cp_info = UsrCPInfo()
        bank_info = UsrCPBank()
        cp_info.startdate = datetime.datetime.now()
        cp_info.enddate = '0000-00-00 00:00:00'
        cp_info.create_time = datetime.datetime.now()

        bank_info.create_time = datetime.datetime.now()    

    #cp info module
    cp_info.loginname = req_args.get('txt_loginname', None)
    cp_info.loginpwd = req_args.get('txt_loginpwd', None)
    cp_info.loginpwd = hash_password(cp_info.loginpwd)
    cp_info.name = req_args.get('name', None)
    cp_info.adminid = req_args.get('business', None)
    cp_info.link_name = req_args.get('link_name', None)
    cp_info.link_email = req_args.get('link_email', None)
    cp_info.link_phone = req_args.get('link_phone', None)
    cp_info.link_qq = req_args.get('link_qq', None)
    cp_info.link_address = req_args.get('link_address', None)
    cp_info.is_show = req_args.get('is_show', False)
    cp_info.content = req_args.get('content', None)
    
    #bank info module
    bank_info.bankname = req_args.get('bank_name', None)
    bank_info.username = req_args.get('bank_username', None)
    bank_info.bankcard = req_args.get('bank_card', None)
    bank_info.is_show = req_args.get('bank_is_show', None)
    bank_info.content = req_args.get('bank_content', None)

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

@operator_view.route("/cooperate/channel/log/", methods=['GET', 'POST'])
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
                                    'channelid': log.channelid, 
                                    'cpid': log.cpid,
                                    'urltype': log.urltype,
                                    'mobile': log.mobile,
                                    'spnumber': log.spnumber,
                                    'momsg': log.momsg,
                                    'linkid': log.linkid,
                                    'tongurl': log.tongurl,
                                    'backmsg': log.backmsg,
                                    'tongdate': log.tongdate,
                                    'is_show': log.is_show,
                                    'create_time': log.create_time
                                    })

            return jsonify({'rows': channel_logs, 'total': total})
        return jsonify({'rows': [], 'total': 0})

@operator_view.route("/operator/status/", methods=['GET'])
@login_required
def operator_status():
    return  render_template('operator_status.html')

@operator_view.route("/operator/demand/", methods=['GET'])
@login_required
def operator_demand():
    return render_template('operator_demand.html')

@operator_view.route("/operator/exploits/", methods=['GET'])
@login_required
def operator_exploits():
    return render_template('operator_exploits.html')

@operator_view.route("/operator/region/", methods=['GET'])
@login_required
def operator_region():
    return render_template('operator_region.html')

@operator_view.route("/operator/purpose/", methods=['GET'])
@login_required
def operator_purpose():
    return render_template('operator_purpose.html')

@operator_view.route("/channel/list/", methods=['GET', 'POST'])
@login_required
def channel_list():
    req_args = request.args if request.method == 'GET' else request.form

    if request.method == 'POST':
        query = g.session.query(ChaInfo).order_by(desc(ChaInfo.id))

        channel_id = req_args.get('channel_id', None)
        sp_id = req_args.get('sp_id', None)
        product_id = req_args.get('product_id', None)
        operator_id = req_args.get('operator_id', None)
        busi_type = req_args.get('busi_type', None)
        area = req_args.get('area', None)
        if channel_id:
            query = query.filter(ChaInfo.id==channel_id)

        if sp_id:
            query = query.filter(ChaInfo.spid==sp_id)

        if product_id:
            query = query.filter(ChaInfo.proid==product_id)

        if operator_id:
            query = query.filter(ChaInfo.operator==operator_id)

        if busi_type:
            query = query.filter(ChaInfo.busi_type==busi_type)

        #if area:
        #    query = query.filter(ChaInfo.busi_type==busi_type)

        channel_list = query.all()
        currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(channel_list)

        channel_list = channel_list[start:(numperpage+start)]

        if channel_list:
            channels = []
            for channel in channel_list:
                channels.append({'id': channel.id, 
                                'cha_name': channel.cha_name,
                                'spid': channel.spid, 
                                'operator': channel.sp_info.name,
                                'product_info': channel.product_info.proname,
                                'busi_info': channel.busi_info.name,
                                'sx': channel.sx,
                                'spnumber': channel.spnumber,
                                'sx_type': channel.sx_type,
                                'price': "￥%s" % channel.price,
                                'costprice': "￥%s" % channel.costprice,
                                'fcpric': "￥%s" % channel.fcpric,
                                'bl': "%s&#37;" % channel.bl,
                                'daymax': channel.daymax,
                                'monmax': channel.monmax,
                                'is_show': channel.is_show,
                                'remark': channel.remark,
                                'content': channel.content,
                                'create_time': channel.create_time
                                })

            return jsonify({'rows': channels, 'total': total})
        return jsonify({'rows': [], 'total': 0})
    else:
        channels = g.session.query(ChaInfo).filter(ChaInfo.is_show==True).all()
        sp_info_list = g.session.query(UsrSPInfo).filter(UsrSPInfo.is_show==True).all()
        products = g.session.query(PubProducts).filter(PubProducts.is_show==True).all()
        busi_list = g.session.query(PubBusiType).filter(PubBusiType.is_show==True).all()

        return render_template('channel_list.html', channels=channels, 
                                            sp_info_list=sp_info_list, 
                                            busi_list=busi_list,
                                            products=products)

@operator_view.route("/channel/add/", methods=['GET', 'POST'])
@operator_view.route("/channel/edit/<channel_id>/", methods=['GET', 'POST'])
@login_required
def channel_add_info(channel_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    city_list = g.session.query(PubCity).all()
    if request.method == 'POST':
        if channel_id:
            channel_info = g.session.query(ChaInfo).filter(ChaInfo.id==channel_id).first()
        else:
            channel_info = ChaInfo()

        channel_info.cha_name = req_args.get('cha_name', None)
        channel_info.spid = req_args.get('sp_info', None)
        channel_info.proid = req_args.get('product', None)
        channel_info.busi_type = req_args.get('busi', None)
        channel_info.operator = req_args.get('operator', None)
        channel_info.sx = req_args.get('txt_sx', None)
        channel_info.spnumber = req_args.get('txt_prot', None)
        channel_info.sx_type = req_args.get('command_type', None)
        channel_info.price = req_args.get('txt_price', 0)
        channel_info.costprice = req_args.get('txt_costprice', 0)
        channel_info.fcpric = req_args.get('txt_fcpric', 0)
        channel_info.bl = req_args.get('txt_bl', 0)
        channel_info.daymax = req_args.get('txt_daymax', 0)
        channel_info.monmax = req_args.get('txt_monmax', 0)
        channel_info.is_show = req_args.get('status_type', False)
        channel_info.remark = req_args.get('content', None)
        channel_info.content = req_args.get('other_content', None)
        channel_info.create_time = datetime.datetime.now()
        provinces = req_args.getlist('province', None)
        black_city = req_args.getlist('city', None)

        try:
            g.session.add(channel_info)
            g.session.commit()

            for prov in provinces:

                cha_province = g.session.query(ChaProvince).filter(ChaProvince.channelid==channel_info.id).\
                                filter(ChaProvince.province==int(prov)).first()

                if not cha_province:
                    cha_province = ChaProvince()
                    cha_province.create_time = datetime.datetime.now()

                cha_province.channelid = channel_info.id
                cha_province.province = int(prov)
                city_str = []
                for _city in black_city:                    
                    for _c in city_list:
                        if _c.id == int(_city) and _c.province == int(prov):
                            city_str.append(_city)

                cha_province.city = ','.join(city_str)
                cha_province.daymax = channel_info.daymax
                cha_province.is_show = channel_info.is_show
                cha_province.content = channel_info.content

                g.session.add(cha_province)
                g.session.commit()

            write_sys_log(2, 
                        u'设置通道信息', 
                        u'用户【%s】在【%s】设置了通道信息，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr), 
                        g.user.id)

            return jsonify({'ok': True})
        except Exception, e:
            print e
            return jsonify({'ok': False, 'errorMsg': u'设置通道失败.'})

    else:
        if channel_id:
            channel_info = g.session.query(ChaInfo).filter(ChaInfo.id==channel_id).first()
        else:
            channel_info = None
        provinces = g.session.query(PubProvince).all()
        products = g.session.query(PubProducts).filter(PubProducts.is_show==True).all()
        busi_list = g.session.query(PubBusiType).filter(PubBusiType.is_show==True).all()
        sp_list = g.session.query(UsrSPInfo).filter(UsrSPInfo.is_show==True).all()
        
        provinces_json = {}
        for prov in provinces:
            provinces_json[prov.id] = []
            prov_item = []
            for city in city_list:
                if city.province == prov.id:
                    prov_item.append({'name': city.city, 'id': city.id})
            provinces_json[prov.id].append(prov_item)

        return render_template('channel_add.html', provinces=provinces, 
                            products=products, 
                            busi_list=busi_list, 
                            sp_list=sp_list,
                            action_url=request.path,
                            provinces_json=json.dumps(provinces_json),
                            channel_info=channel_info)

@operator_view.route("/channel/confige/", methods=['GET', 'POST'])
@operator_view.route("/channel/confige/<channel_id>/", methods=['GET', 'POST'])
@login_required
def channel_confige(channel_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    action_path = request.path

    if request.method == 'GET':
        channel_list = g.session.query(ChaInfo).filter(ChaInfo.is_show==True).all()
        cp_info_list = g.session.query(UsrCPInfo).filter(UsrCPInfo.is_show==True).all()
        admins = g.session.query(SysAdmin).filter(SysAdmin.is_show==True).all()
        provinces = g.session.query(PubProvince).all()
        city_list = g.session.query(PubCity).all()

        provinces_json = {}

        for prov in provinces:
            provinces_json[prov.id] = []
            prov_item = []
            for city in city_list:
                if city.province == prov.id:
                    prov_item.append({'name': city.city, 'id': city.id})
            provinces_json[prov.id].append(prov_item)

        if not channel_id:
            channel_id = 0

        return render_template('channel_allocated.html', 
                                provinces=provinces,
                                action_path=action_path, 
                                channel_id=int(channel_id),
                                channel_list=channel_list,
                                admins=admins,
                                provinces_json=json.dumps(provinces_json),
                                cp_info_list=cp_info_list)
    else:

        query = g.session.query(UsrChannel).order_by(desc(UsrChannel.id))

        ch_id = req_args.get('channel_id', None)
        cp_id = req_args.get('cp_id', None)
        status = req_args.get('status', None)
        other_query = req_args.get('other_query', None)
        keyword = req_args.get('keyword', None)

        if status:
            query = query.filter(UsrChannel.is_show==status)

        if ch_id:
            query = query.filter(UsrChannel.channelid==ch_id)
        else:
            if channel_id:
                query = query.filter(UsrChannel.channelid==channel_id)

        if cp_id:
            query = query.filter(UsrChannel.cpid==cp_id)

        
        if other_query:
            if other_query == 'spnumber':
                query = query.filter(UsrChannel.spnumber==keyword)

            if other_query == 'backurl':
                query = query.filter(UsrChannel.backurl==keyword)

        channel_allocated_list = query.all()

        currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))
        start = numperpage * (currentpage - 1)
        total = len(channel_allocated_list)

        channel_allocated_list = channel_allocated_list[start:(numperpage+start)]

        if channel_allocated_list:
            channels = []
            for channel in channel_allocated_list:
                channels.append({'id': channel.id,
                                'channel_name': '[%s] %s' % (channel.cha_info.id, channel.cha_info.cha_name), 
                                'cp_name': '[%s] %s' % (channel.cp_info.id, channel.cp_info.name),
                                'sx_str': u'%s 到 %s' % (channel.momsg, channel.spnumber),
                                'rysc_url': channel.backurl,
                                'is_show': channel.is_show
                                })

            return jsonify({'rows': channels, 'total': total})
        return jsonify({'rows': [], 'total': 0})

@operator_view.route("/channel/info/get/", methods=['GET'])
@login_required
def  channel_info_get():
    req_args = request.args if request.method == 'GET' else request.form
    channel_id = req_args.get('channel_id', None)
    if channel_id:
        channel = g.session.query(ChaInfo).filter(ChaInfo.id == channel_id).one()
        if channel:
            return jsonify({'ok': True, 'data': {'msg': channel.sx, 
                                                'spnumber': channel.spnumber, 
                                                'fcprice': channel.fcpric,
                                                'bl': channel.bl}
                            })
        else:
            return jsonify({'ok': False})
    else:
        return jsonify({'ok': False})


@operator_view.route("/channel/confige/set/", methods=["POST"])
@operator_view.route("/channel/confige/set/<allocated_id>/", methods=["GET", "POST"])
@login_required
def set_channel_allocated(allocated_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    if request.method == "GET":
        if allocated_id:
            channel_allocated = g.session.query(UsrChannel).filter(UsrChannel.id==allocated_id).one()
            user_province = []

            if channel_allocated:
                for province in channel_allocated.usr_province:
                    user_province.append(province.province)
                
                print user_province
                return jsonify({'ok': True, 'data': {
                        'channel': channel_allocated.channelid,
                        'sys_admin': channel_allocated.adminid,
                        'cp': channel_allocated.cpid,
                        'rad_status':1 if channel_allocated.is_show else 0,
                        'txt_momsg': channel_allocated.momsg,
                        'txt_spnumber': channel_allocated.spnumber,
                        'txt_fcprice': channel_allocated.fcprice,
                        'txt_bl': channel_allocated.bl,
                        'rad_sx_type': channel_allocated.sx_type,
                        'txt_backurl': channel_allocated.backurl,
                        'content': channel_allocated.content,
                        'allocated_province': user_province
                        }
                    })
        else:
            return jsonify({'ok': False})
    else:
        if allocated_id:
            channel_allocated = g.session.query(UsrChannel).filter(UsrChannel.id==allocated_id).one()
        else:
            channel_allocated = UsrChannel()
            channel_allocated.create_time = datetime.datetime.now()
        
        channel_allocated.channelid = req_args.get("channel", None)
        channel_allocated.cpid = req_args.get("cp", None)
        channel_allocated.adminid = req_args.get("sys_admin", None)
        channel_allocated.momsg = req_args.get("txt_momsg", None)
        channel_allocated.sx_type = req_args.get("rad_sx_type", None)
        channel_allocated.spnumber = req_args.get("txt_spnumber", None)
        channel_allocated.fcprice = req_args.get("txt_fcprice", None)
        channel_allocated.bl = req_args.get("txt_bl", None)
        channel_allocated.backurl = req_args.get("txt_backurl", None)
        channel_allocated.is_show = req_args.get("rad_status", False)
        channel_allocated.content = req_args.get("content", None)
        try:
            write_sys_log(2, 
                    u'分配通道渠道', 
                    u'用户【%s】在【%s】分配通道渠道，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr), 
                    g.user.id)
            g.session.add(channel_allocated)
            g.session.commit()
            return jsonify({'ok': True})
        except Exception, e:
            print e
            return jsonify({'errorMsg': 'error'})

@operator_view.route("/channel/confige/status/set/", methods=["POST"])
@login_required
def channel_config_status_set():
    req_args = request.args if request.method == 'GET' else request.form
    if request.method == 'POST':
        change_type = req_args.get("change_type", None)
        status = req_args.get("status", None)
        channel_id = req_args.get('channel_id', None)
        allocated_id = req_args.get('allocated_id', None)
        if change_type == 'channel':
            change_module = g.session.query(ChaInfo).filter(ChaInfo.id==channel_id).one()
        else:
            change_module = g.session.query(UsrChannel).filter(UsrChannel.id==allocated_id).one()
        
        change_module.is_show = status
        try:
            write_sys_log(2, 
                    u'通道状态设置', 
                    u'用户【%s】在【%s】分配通道渠道，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr), 
                    g.user.id)
            g.session.add(change_module)
            g.session.commit()
            return jsonify({'ok': True})
        except Exception, e:
            print e
            return jsonify({'errorMsg': 'error'})

@operator_view.route("/channel/settings/", methods=['GET'])
@login_required
def channel_settings():
    return render_template('channel_settings.html')

@operator_view.route("/channel/sync/", methods=['GET'])
@login_required
def channel_sync():
    return render_template('channel_sync.html')

@operator_view.route("/channel/cover/", methods=['GET'])
@login_required
def channel_cover():
    return render_template('channel_cover.html')

@operator_view.route("/financial/cooperate/detail/", methods=['GET'])
@login_required
def financial_cooperate_detail():
    return render_template('financial_cooperate_detail.html')

@operator_view.route("/financial/channel/detail/", methods=['GET'])
@login_required
def financial_channel_detail():
    return render_template('financial_channel_detail.html')


@operator_view.route("/financial/cooperate/summary/", methods=['GET'])
@login_required
def financial_cooperate_summary():
    return render_template('financial_cooperate_summary.html')

@operator_view.route("/financial/channel/summary/", methods=['GET'])
@login_required
def financial_channel_summary():
    return render_template('financial_channel_summary.html')

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

@operator_view.route("/sys/black/", methods=['GET', 'POST'])
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

@operator_view.route("/sys/get/city/", methods=['GET', 'POST'])
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

@operator_view.route("/sys/black/add/", methods=['GET', 'POST'])
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
