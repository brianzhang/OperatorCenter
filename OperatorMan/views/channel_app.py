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

channel_view = Blueprint('channel_view', __name__, url_prefix='/channel')

@channel_view.route("/list/", methods=['GET', 'POST'])
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
                                'channel_name': channel.cha_name,
                                'operator_info': "[%s] %s" % (channel.spid, channel.sp_info.name),
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
        channels = g.session.query(ChaInfo).all()
        sp_info_list = g.session.query(UsrSPInfo).all()
        products = g.session.query(PubProducts).all()
        busi_list = g.session.query(PubBusiType).all()

        return render_template('channel_list.html', channels=channels, 
                                            sp_info_list=sp_info_list, 
                                            busi_list=busi_list,
                                            products=products)

@channel_view.route("/add/", methods=['GET', 'POST'])
@channel_view.route("/edit/<channel_id>/", methods=['GET', 'POST'])
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
        products = g.session.query(PubProducts).all()
        busi_list = g.session.query(PubBusiType).all()
        sp_list = g.session.query(UsrSPInfo).all()
        
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

@channel_view.route("/confige/", methods=['GET', 'POST'])
@channel_view.route("/confige/<channel_id>/", methods=['GET', 'POST'])
@login_required
def channel_confige(channel_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    action_path = request.path

    if request.method == 'GET':
        channel_list = g.session.query(ChaInfo).all()
        cp_info_list = g.session.query(UsrCPInfo).all()
        admins = g.session.query(SysAdmin).all()
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

@channel_view.route("/info/get/", methods=['GET'])
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


@channel_view.route("/confige/set/", methods=["POST"])
@channel_view.route("/confige/set/<allocated_id>/", methods=["GET", "POST"])
@login_required
def set_channel_allocated(allocated_id=None):
    req_args = request.args if request.method == 'GET' else request.form
    city_list = g.session.query(PubCity).all()
    if request.method == "GET":
        if allocated_id:
            channel_allocated = g.session.query(UsrChannel).filter(UsrChannel.id==allocated_id).one()
            user_province = []
            city_html = ""
            if channel_allocated:
                for province in channel_allocated.usr_province:
                    user_province.append(province.province)
                    _citys = g.session.query(PubCity).filter(PubCity.province==province.province).all()
                    if _citys:
                        city_html += """<div id="allocated_cits_%s" style="line-height: 24px;">%s: """  % (province.province, province.province_info.province)
                        for _city in _citys:
                            city_html += """
                                <label><input type="checkbox" province="%s" value="%s" name="city"/>%s</label>
                            """ % (province.province, _city.id, _city.city)
                        city_html += """</div>"""
                
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
                        'allocated_province': user_province,
                        "city_html": city_html
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
        provinces = req_args.getlist('allocated_province', None)
        black_city = req_args.getlist('city', None)

        try:
            write_sys_log(2, 
                    u'分配通道渠道', 
                    u'用户【%s】在【%s】分配通道渠道，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr), 
                    g.user.id)
            g.session.add(channel_allocated)
            g.session.commit()

            for prov in provinces:

                g.session.query(UsrProvince).filter(UsrProvince.channelid==channel_allocated.id).\
                                filter(UsrProvince.province==int(prov)).delete()

                usr_province = UsrProvince()
                usr_province.channelid = channel_allocated.id
                usr_province.cpid = channel_allocated.cpid
                usr_province.adminid = g.user.id
                usr_province.create_time = datetime.datetime.now()
                usr_province.province = int(prov)
                usr_province.daymax = 1000
                usr_province.is_show = channel_allocated.is_show
                usr_province.content = channel_allocated.content
                city_str = []
                for _city in black_city:                    
                    for _c in city_list:
                        if _c.id == int(_city) and _c.province == int(prov):
                            city_str.append(_city)

                usr_province.city = ','.join(city_str)
                g.session.add(usr_province)
                g.session.commit()

            return jsonify({'ok': True})
        except Exception, e:
            print e
            return jsonify({'errorMsg': 'error'})

@channel_view.route("/confige/status/set/", methods=["POST"])
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

        elif change_type == 'sync_settings':
            change_module = g.session.query(UsrChannelSync).filter(UsrChannelSync.id==channel_id).one()

        elif change_type == 'sync':
            change_module = g.session.query(UsrSPSync).filter(UsrSPSync.id==channel_id).one()

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
           
            return jsonify({'errorMsg': 'error'})

@channel_view.route("/settings/", methods=['GET', 'POST'])
@login_required
def channel_settings():
    #channels
    req_args = request.args if request.method == 'GET' else request.form
    if request.method == "GET":
        channels = g.session.query(ChaInfo).all()
        return render_template('channel_settings.html', channels=channels)
    else:
        query = g.session.query(UsrChannelSync).order_by(desc(UsrChannelSync.id))

    	channel_id = req_args.get("channel_id", None)
    	sync_type = req_args.get("sync_type", None)
    	status = req_args.get("status", None)

        if channel_id:
            query = query.filter(UsrChannelSync.channelid==channel_id)

        if sync_type:
            query = query.filter(UsrChannelSync.sync_type==sync_type)

        if status:
            query = query.filter(UsrChannelSync.is_show==status)

        usr_channel_sync_list = query.all()

    	currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))        
        start = numperpage * (currentpage - 1)
        total = len(usr_channel_sync_list)

        usr_channel_sync_list = usr_channel_sync_list[start:(numperpage+start)]

        if usr_channel_sync_list:
            usr_channels = []
            for usr_sync in usr_channel_sync_list:
                usr_channels.append({
                        "id": usr_sync.id,
                        "channel_name": "[%s] %s" % (usr_sync.cha_info.id, usr_sync.cha_info.cha_name),
                        "sync_type": usr_sync.sync_type,
                        "url": usr_sync.url,
                        "status_key": usr_sync.status_key,
                        "is_rsync": usr_sync.is_rsync,
                        "is_show": usr_sync.is_show
                    })
            return jsonify({'rows': usr_channels, 'total': total})
        else:
            return jsonify({'rows': [], 'total': 0})

@channel_view.route("/settings/add/", methods=["GET", "POST"])
@channel_view.route("/settings/edit/<c_id>/", methods=["GET", "POST"])
@login_required
def channel_settings_edit(c_id=None):
    req_args = request.args if request.method == 'GET' else request.form

    if c_id:
        channel_setting_info = g.session.query(UsrChannelSync).filter(UsrChannelSync.id==c_id).one()
    else:
        channel_setting_info = UsrChannelSync()
        channel_setting_info.create_time = datetime.datetime.now()

    
    channel_setting_info.channelid = req_args.get('channelid', None)
    channel_setting_info.sync_type = req_args.get("sync_type", None)
    channel_setting_info.status_key = req_args.get("status_key", None)
    channel_setting_info.url = req_args.get("url", None)
    channel_setting_info.is_rsync = req_args.get("is_rsync", False)
    channel_setting_info.is_show = req_args.get("is_show", False)
    channel_setting_info.spnumber = '0'
    channel_setting_info.mobile = '0'
    channel_setting_info.linkid = '0'
    channel_setting_info.msg = '0'

    try:
        write_sys_log(2, 
                    u'接口配置', 
                    u'用户【%s】在【%s】分配接口配置，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr), 
                    g.user.id)

        g.session.add(channel_setting_info)
        g.session.commit()
        return jsonify({'ok': True})

    except Exception, e:
        return jsonify({'errorMsg': u'添加失败'})


@channel_view.route("/sync/", methods=['GET', 'POST'])
@login_required
def channel_sync():

    #channels
    req_args = request.args if request.method == 'GET' else request.form
    if request.method == "GET":
        spinfo_list = g.session.query(UsrSPInfo).all()
        channels = g.session.query(ChaInfo).all()
        return render_template('channel_sync.html', spinfo_list=spinfo_list, channels=channels)
    else:
        query = g.session.query(UsrSPSync).order_by(desc(UsrSPSync.id))

        spid = req_args.get("spid", None)
        sync_type = req_args.get("sync_type", None)
        status = req_args.get("status", None)

        if spid:
            query = query.filter(UsrSPSync.spid==spid)

        if sync_type:
            query = query.filter(UsrSPSync.sync_type==sync_type)

        if status:
            query = query.filter(UsrSPSync.is_show==status)

        usr_channel_sync_list = query.all()

        currentpage = int(req_args.get('page', 1))
        numperpage = int(req_args.get('rows', 20))        
        start = numperpage * (currentpage - 1)
        total = len(usr_channel_sync_list)

        usr_channel_sync_list = usr_channel_sync_list[start:(numperpage+start)]

        if usr_channel_sync_list:
            usr_channels = []
            for usr_sync in usr_channel_sync_list:
                usr_channels.append({
                        "id": usr_sync.id,
                        "channel_name": "[%s] %s" % (usr_sync.cha_info.id, usr_sync.cha_info.cha_name),
                        "sp_name": "[%s] %s" % (usr_sync.usr_spinfo.id, usr_sync.usr_spinfo.name),
                        "sync_type": usr_sync.sync_type,
                        "url": usr_sync.url,
                        "status_key": usr_sync.status_key,
                        "is_rsync": usr_sync.is_rsync,
                        "is_show": usr_sync.is_show
                    })
            return jsonify({'rows': usr_channels, 'total': total})
        else:
            return jsonify({'rows': [], 'total': 0})

@channel_view.route("/sync/add/", methods=["POST"])
@channel_view.route("/sync/<sync_id>/", methods=["POST"])
def sync_add(sync_id=None):
    req_args = request.args if request.method == 'GET' else request.form

    if sync_id:
        channel_sync_info = g.session.query(UsrSPSync).filter(UsrSPSync.id==sync_id).one()
    else:
        channel_sync_info = UsrSPSync()
        channel_sync_info.create_time = datetime.datetime.now()

    
    channel_sync_info.spid = req_args.get('spid', None)
    channel_sync_info.channelid = req_args.get('channelid', None)
    channel_sync_info.sync_type = req_args.get("sync_type", None)
    channel_sync_info.status_key = req_args.get("status_key", None)
    channel_sync_info.url = req_args.get("url", None)
    channel_sync_info.is_rsync = req_args.get("is_rsync", False)
    channel_sync_info.is_show = req_args.get("is_show", False)
    channel_sync_info.spnumber = req_args.get("spnumber", 0)
    channel_sync_info.mobile = req_args.get("mobile", 0)
    channel_sync_info.linkid = req_args.get("linkid", 0)
    channel_sync_info.msg = req_args.get("msg", 0)

    try:
        write_sys_log(2, 
                    u'同步地址', 
                    u'用户【%s】在【%s】分配同步地址，登录IP为：【%s】'%(g.user.realname, datetime.datetime.now(), request.remote_addr), 
                    g.user.id)

        g.session.add(channel_sync_info)
        g.session.commit()
        return jsonify({'ok': True})

    except Exception, e:
        return jsonify({'errorMsg': u'添加失败'})


@channel_view.route("/cover/", methods=['GET'])
@login_required
def channel_cover():
    provinces = g.session.query(PubProvince).all()
    channels = g.session.query(ChaInfo).all()
    render_data = []

    for province in provinces:
        _item = {'province': province.province, 'id': province.id}
        _channels1 = []
        _channels2 = []
        _channels3 = []
        for channel in channels:

            for p in channel.cha_province:

                if p.province_info.id == province.id and channel.operator == '0':
                    _channels1.append({'id':channel.id, 'cha_name': channel.cha_name, 'operator': channel.operator})

                if p.province_info.id == province.id and channel.operator == '1':
                    _channels2.append({'id':channel.id, 'cha_name': channel.cha_name, 'operator': channel.operator})

                if p.province_info.id == province.id and channel.operator == '2':
                    _channels3.append({'id':channel.id, 'cha_name': channel.cha_name, 'operator': channel.operator})

        _item['channels1']=_channels1
        _item['channels2']=_channels2
        _item['channels3']=_channels3
        
        render_data.append(_item)

    return render_template('channel_cover.html', render_data=json.dumps(render_data))