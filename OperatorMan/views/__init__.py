# coding=utf8
'''
Created on 2014-05-19
@author: brian
'''
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import datetime
import calendar
import time
import hashlib, hmac, re
import string
import random
from flask import jsonify, request, session, redirect, g
from functools import wraps
from pyExcelerator import *
from sqlalchemy import or_, desc, func, distinct, CHAR, sql

from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync
from OperatorMan.configs import settings

def _jsonify(status, code='', data={}):
    return jsonify(ok=status, reason=code, data=data)

def ok_json(code='', data={}):
    return _jsonify(True, code, data)

def fail_json(code='', data={}):
    return _jsonify(False, code, data)

def hash_password(password):
    m = hmac.new(settings.SECRET_KEY, password, hashlib.sha1)
    return m.hexdigest()

def random_key(size=6, chars=string.ascii_uppercase + string.digits):
    size = 6
    return ''.join(random.choice(chars) for _ in range(size))

def write_sys_log(_type, _title, _content, _uid):
    get_session = create_operator_session()
    sys_log = SysAdminLog()
    sys_log.adminid = _uid
    sys_log.op_type = _type
    sys_log.op_title = _title
    sys_log.op_content = _content
    sys_log.create_time = datetime.datetime.now()

    try:
        get_session.add(sys_log)
        get_session.commit()
        return True
    except Exception, e:
        get_session.rollback()
        return False

def get_send_html(status=None, kill_key=None):
    
    _status_lab = u'<span style="color:chartreuse">成功</span>' if status else u'<span style="color:red">失败</span>'
    _kill_lab = ''
    if int(kill_key) == 0:
        _kill_lab = u'<span style="color:chartreuse">下发</span>'
    elif kill_key == 1:
        _kill_lab = u'<span style="color:red">扣量</span>'
    elif kill_key == 2:
        _kill_lab = u'<span style="color:chocolate">屏蔽</span>'
    elif kill_key == 3:
        _kill_lab = u'<span style="color:blueviolet">黑名单</span>'
    elif kill_key == 4:
        _kill_lab = u'<span style="color:darkgreen">失败</span>'
    elif kill_key == 5:
        _kill_lab = u'<span style="color:darkgreen">未发</span>'
    else:
        _kill_lab = u'<span style="color:darkgreen">失败</span>'
    return '%s|%s' % (_kill_lab, _status_lab)

def query_stats_data(req=None):
    data_list = []
    footers = []
    if req:
        order_type = req.get('order_type', 'time')
        
        today = datetime.datetime.today()
        _month = today.month if today.month >10 else '0%s' % today.month
        _day = today.day if today.day >10 else '0%s' % today.day
        regdate = "%s%s%s" % (today.year, _month, _day)        

        time = req.get('time', regdate)
        month = req.get('month', None)
        year = req.get('year', None)
        channelid = req.get('channel_id', None)
        sp_id = req.get("sp_id", None)
        

        query_data = g.session.query(func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp'))

        user_count = g.session.query(DataMr.reghour, func.count(distinct(DataMr.mobile)).label('user_count'))

        if channelid:
          query_data = query_data.filter(DataEverday.channelid==channelid)
          user_count = user_count.filter(DataMr.channelid==channelid)
        if sp_id:
          query_data = query_data.filter(ChaInfo.spid==sp_id)
          user_count = user_count.filter(ChaInfo.spid==sp_id)

        if order_type:
          if time and order_type == 'time':
            time = time.replace('-', '')
            query_data = query_data.add_column(DataEverday.tj_hour.label('has_index')).filter(DataEverday.tj_date == time).group_by(DataEverday.tj_hour)
            user_count = user_count.add_column(DataMr.reghour.label('has_index')).filter(DataMr.regdate==time).group_by(DataMr.reghour)

          if month and year and order_type == 'month':
            _month_s = '%s%s01' % (year, month)
            _month_e = '%s%s31' % (year, month)

            query_data = query_data.add_column(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(8)')).label('has_index')).\
                        filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).\
                        group_by(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(8)')))

            user_count = user_count.add_column(func.convert(DataMr.regdate, sql.literal_column('CHAR(8)')).label('has_index')).\
                        filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(func.convert(DataMr.regdate, sql.literal_column('CHAR(8)')))

          if year and not month and order_type == 'year':
            _month_s = '%s0101' % year
            _month_e = '%s1231' % year

            query_data = query_data.add_column(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(6)')).label('has_index')).filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).group_by(func.convert(DataEverday.tj_date, sql.literal_column('CHAR(6)')))
            user_count = user_count.add_column(func.convert(DataMr.regdate, sql.literal_column('CHAR(6)')).label('has_index')).\
                        filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(func.convert(DataMr.regdate, sql.literal_column('CHAR(6)')))

        query_data = query_data.all()
        user_count = user_count.all()

        range_date = 24
        if order_type and order_type == 'time':
            range_date = 24

        if month and year and order_type == 'month':
            range_date = calendar.monthrange(int(year), int(month))
            range_date = range_date[1]+1

        if year and not month and order_type == 'year':
          range_date = 13

        for i in range(0, range_date-1):
            _timer = '%s:00 - %s:00' % (i, i+1) if order_type=='time' else '%s' % (i+1)
            if order_type=='time':
                _timer = '%s:00 - %s:00' % (i, i+1)
            elif order_type == 'month':
                _timer = u'%s 号' % (i+1)
            else:
                _timer = u'%s 月' % (i+1)
            data_list.append({
                'timer': _timer,
                'mo_all': 0,
                'mr_all': 0,
                't_customize': 0,
                't_conversion_rate': 0,
                'conversion_rate': 0,
                'into_rate': 0,
                'arpu': 0
            })
        if order_type=='time':
            _timer = '%s:00 - %s:00' % (23, 0)
            data_list.append({
                'timer': _timer,
                'mo_all': 0,
                'mr_all': 0,
                't_customize': 0,
                't_conversion_rate': 0,
                'conversion_rate': 0,
                'into_rate': 0,
                'arpu': 0
            })
            
        if query_data:
            _mo_all = 0
            _t_customize = 0
            _t_conversion_rate = 0
            _conversion_rate = 0
            _into_rate = 0
            for item in query_data:
                _index = 0
                if order_type == 'time':
                  _index = item.has_index
                if order_type == 'month':
                    _year_month = int('%s%s' % (year, month))
                    _index = int(item.has_index) % _year_month
                if order_type == 'year':
                    _index = int(item.has_index) % int(year)
                _index -= 1
                data_master = data_list[_index]
                t_customize = item.mr_all
                item.mo_all = item.mo_all if item.mo_all > 0 else 1
                item.mr_all = item.mr_all if item.mr_all > 0 else 1
                t_conversion_rate = float(item.mr_all) / float(item.mo_all)
                t_conversion_rate = float("%.2f" % t_conversion_rate)
                conversion_rate = float(item.mr_cp) / float(item.mr_all)
                conversion_rate = float("%.2f" % conversion_rate)
                into_rate= float(item.mr_cp) / float(item.mr_all)
                into_rate= float("%.2f" % into_rate)

                _t_customize += t_customize
                _mo_all += item.mo_all
                _t_conversion_rate += t_conversion_rate
                _conversion_rate += conversion_rate
                _into_rate += into_rate

                data_master['mo_all'] = item.mo_all
                data_master['mr_all'] = item.mr_all
                data_master['t_customize'] = t_customize
                data_master['t_conversion_rate'] = t_conversion_rate
                data_master['conversion_rate'] = conversion_rate
                data_master['into_rate'] = into_rate
                
                for u in user_count:
                    if u.has_index == item.has_index:
                        _arpu = float(item.mr_all) / float(u.user_count)
                        data_master['arpu'] =  float("%.2f" % _arpu)

            footers.append({
                'timer': u'汇总',
                'mo_all': _mo_all,
                't_customize': float("%.2f" %  _t_customize),
                't_conversion_rate': float("%.2f" %  _t_conversion_rate),
                'conversion_rate': float("%.2f" %  _conversion_rate),
                'into_rate': float("%.2f" %  _into_rate),
                'arpu': '--'
            })
            return {'rows': data_list, 'ok': True, 'order_type': order_type, 'footer': footers}
        else:
            footers.append({
                'timer': u'汇总',
                'mo_all': 0,
                't_customize': 0,
                't_conversion_rate': 0,
                'conversion_rate': 0,
                'into_rate': 0,
                'arpu': '--'
            })
            return {'rows': data_list, 'ok': False, 'order_type': order_type, 'footer': footers}

def query_province_stats(req=None):
    data_list = []
    footers = []
    if req:
        
        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s%s%s" % (today.year, _month, _day)

        order_type = req.get('order_type', 'day')

        time = req.get('day', regdate)
        month = req.get('month', None)
        year = req.get('year', None)
        channelid = req.get('channel_id', None)
        sp_id = req.get("sp_id", None)
        

        query_data = g.session.query(func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp'), DataEverday.province)

        user_count = g.session.query(DataMr.province, func.count(distinct(DataMr.mobile)).label('user_count'))


        if channelid:
          query_data = query_data.filter(DataEverday.channelid==channelid)
          user_count = user_count.filter(DataMr.channelid==channelid)
        if sp_id:
          query_data = query_data.filter(ChaInfo.spid==sp_id)
          user_count = user_count.filter(ChaInfo.spid==sp_id)

        if order_type:
          if time and order_type == 'day':
            time = time.replace('-', '')
            query_data = query_data.add_column(DataEverday.tj_date.label('has_index')).filter(DataEverday.tj_date == time).group_by(DataEverday.province)
            user_count = user_count.add_column(DataMr.regdate.label('has_index')).filter(DataMr.regdate==time).group_by(DataMr.province)

          if month and year and order_type == 'month':
            _month_s = '%s%s01' % (year, month)
            _month_e = '%s%s31' % (year, month)

            query_data = query_data.filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).\
                        group_by(DataEverday.province)

            user_count = user_count.filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(DataMr.province)

          if year and not month and order_type == 'year':
            _month_s = '%s0101' % year
            _month_e = '%s1231' % year

            query_data = query_data.filter(DataEverday.tj_date >= _month_s).filter(DataEverday.tj_date <= _month_e).group_by(DataEverday.province)
            user_count = user_count.filter(DataMr.regdate >= _month_s).\
                        filter(DataMr.regdate <= _month_e).\
                        group_by(DataMr.province)

        query_data = query_data.all()
        user_count = user_count.all()

        
        for i in range(0, 31):
            data_list.append({
                'province': settings.PROVINCE[i],
                'mo_all': 0,
                'mr_all': 0,
                't_customize': 0,
                't_conversion_rate': 0,
                'conversion_rate': 0,
                'into_rate': 0,
                'arpu': 0
            })

        _mo_all = 0
        _t_customize = 0
        _t_conversion_rate = 0
        _conversion_rate = 0
        _into_rate = 0
        if query_data:
            for item in query_data:
                _index = item.province - 1
                try:
                    data_master = data_list[_index]
                except Exception, e:
                    pass

                t_customize = item.mr_all
                item.mo_all = item.mo_all if item.mo_all > 0 else 1
                item.mr_all = item.mr_all if item.mr_all > 0 else 1
                t_conversion_rate = float(item.mr_all) / float(item.mo_all)
                t_conversion_rate = float("%.2f" % t_conversion_rate)
                conversion_rate = float(item.mr_cp) / float(item.mr_all)
                conversion_rate = float("%.2f" % conversion_rate)
                into_rate= float(item.mr_cp) / float(item.mo_all)
                into_rate= float("%.2f" % into_rate)

                data_master['mo_all'] = item.mo_all
                data_master['mr_all'] = item.mr_all
                data_master['t_customize'] = t_customize
                data_master['t_conversion_rate'] = t_conversion_rate
                data_master['conversion_rate'] = conversion_rate
                data_master['into_rate'] = into_rate

                _t_customize += t_customize
                _mo_all += item.mo_all
                _t_conversion_rate += t_conversion_rate
                _conversion_rate += conversion_rate
                _into_rate += into_rate

                for u in user_count:
                    if u.province == item.province:
                        arpu = float(item.mr_all) / float(u.user_count)
                        data_master['arpu'] = float("%.2f" % arpu)
        footers.append({
                'province': u'汇总',
                'mo_all': _mo_all,
                't_customize': float("%.2f" % _t_customize),
                't_conversion_rate': float("%.2f" % _t_conversion_rate),
                'conversion_rate': float("%.2f" % _conversion_rate),
                'into_rate': float("%.2f" % _into_rate),
                'arpu': '--'
        })
        return {'rows': data_list, 'ok': True, 'order_type': order_type, 'footer': footers}
    else:
        return {'rows': data_list, 'ok': False, 'order_type': order_type, 'footer': footers}

def query_channel_status(req):
    data_list = []
    footers = []
    totlal = 0
    if req:

        today = datetime.datetime.today()
        _month = today.month if today.month > 10 else '0%s' % today.month
        _day = today.day if today.day > 10 else '0%s' % today.day
        regdate = "%s-%s-%s" % (today.year, _month, _day)
        date_time = req.get('date_time', regdate)
        query_data = g.session.query(DataEverday, func.sum(DataEverday.mo_all).label('mo_all'), \
                                    func.sum(DataEverday.mr_all).label('mr_all'), \
                                    func.sum(DataEverday.mr_cp).label('mr_cp'), DataEverday.channelid)
        date_time = date_time.replace('-', '')
        user_count = g.session.query(DataMr.channelid, func.count(distinct(DataMr.mobile)).label('user_count'))
        query_data = query_data.add_column(DataEverday.tj_date.label('has_index')).filter(DataEverday.tj_date == date_time).group_by(DataEverday.channelid)
        user_count = user_count.add_column(DataMr.regdate.label('has_index')).filter(DataMr.regdate==date_time).group_by(DataMr.channelid)
        
        query_data = query_data.all()
        user_count = user_count.all()
        
        if query_data:
            _mo_all = 0
            _t_customize = 0
            _t_conversion_rate = 0
            _conversion_rate = 0
            _into_rate = 0
            totlal = len(query_data)
            for item in query_data:
                #print '======================================'
                #print item.mo_all
                #print item.mr_all
                #print item.mr_cp
                #print item.has_index
                #print item[0].channe_info.sp_info.id
                #print '======================================'
                data_master = {}
                t_customize = item.mr_all
                item.mo_all = item.mo_all if item.mo_all > 0 else 1
                item.mr_all = item.mr_all if item.mr_all > 0 else 1
                t_conversion_rate = float(item.mr_all) / float(item.mo_all)
                t_conversion_rate = float("%.2f" % t_conversion_rate)
                conversion_rate = float(item.mr_cp) / float(item.mr_all)
                conversion_rate = float("%.2f" % conversion_rate)
                into_rate= float(item.mr_cp) / float(item.mo_all)
                into_rate= float("%.2f" % into_rate)
                data_master['sp_info'] =  "[%s]%s" % (item[0].channe_info.sp_info.id, item[0].channe_info.sp_info.name)
                data_master['channel'] = "[%s]%s" % (item[0].channe_info.id, item[0].channe_info.cha_name)
                data_master['mo_all'] = item.mo_all
                data_master['mr_all'] = item.mr_all
                data_master['t_customize'] = t_customize
                data_master['t_conversion_rate'] = t_conversion_rate
                data_master['conversion_rate'] = conversion_rate
                data_master['into_rate'] = into_rate

                _t_customize += t_customize
                _mo_all += item.mo_all
                _t_conversion_rate += t_conversion_rate
                _conversion_rate += conversion_rate
                _into_rate += into_rate

                for u in user_count:
                    if u.channelid == item[0].channelid:
                        arpu = float(item.mr_all) / float(u.user_count)
                        data_master['arpu'] = float("%.2f" % arpu)
                data_list.append(data_master)

            footers.append({
                'sp_info': u'汇总',
                'mo_all': _mo_all,
                't_customize': float("%.2f" % _t_customize),
                't_conversion_rate': float("%.2f" % _t_conversion_rate),
                'conversion_rate': float("%.2f" % _conversion_rate),
                'into_rate': float("%.2f" % _into_rate),
                'arpu': '--'
            })
        return {'rows': data_list, 'ok': True,  'footer': footers, 'total': totlal}
    else:
        return {'rows': data_list, 'ok': False, 'footer': footers, 'total': totlal}


def execl_import(data=None, title=None, tab_name=None,account_name=None, bank_name=None, account=None, sp_name=None, summerize_data=None):    
    tab_name = tab_name
    bank_name = bank_name
    account_name = account_name
    account = account
    sp_name = sp_name
    summerize_data = summerize_data
    
    borders = Borders()  
    borders.left = 1  
    borders.right = 1  
    borders.top = 1  
    borders.bottom = 1
    
    al = Alignment()  
    al.horz = Alignment.HORZ_CENTER  
    al.vert = Alignment.VERT_CENTER
    
    fnt = Font()
    fnt.height = 320
    fnt.name = u'楷体'
    fnt.bold = True
    
    title_style = XFStyle()  
    title_style.borders = borders  
    title_style.alignment = al
    title_style.font = fnt
    
    fnt1 = Font()
    fnt1.height = 280
    fnt1.name = u'楷体'
    fnt1.bold = False
    
    fnt2 = Font()
    fnt2.height = 280
    fnt2.name = u'楷体'
    fnt2.bold = True
    
    text_style = XFStyle()
    text_style.borders = borders
    text_style.font = fnt1
    text_style.num_format_str = '0.00'
    
    tab_head_style = XFStyle()
    tab_head_style.borders = borders
    tab_head_style.font = fnt2
    tab_head_style.alignment = al
    
    w = Workbook()
    ws = w.add_sheet(u"%s" % (tab_name))
    ws.write_merge(0, 0, 0, 6, title, title_style)
    ws.write_merge(1, 1, 0, 4, '%s ' % (sp_name), text_style)
    ws.write_merge(1, 1, 5, 6, u'账期：%s ' % (summerize_data), text_style)
    ws.write(2, 0, u"通道", tab_head_style)
    ws.write(2, 1, u"资费", tab_head_style)
    ws.write(2, 2, u"条数/分钟数", tab_head_style)
    ws.write(2, 3, u"单价", tab_head_style)
    ws.write(2, 4, u"金额", tab_head_style)
    ws.write(2, 5, u"退费", tab_head_style)
    ws.write(2, 6, u"实际结算金额", tab_head_style)
    ws.col(0).width = 3 * 0x0d00
    ws.col(1).width = 40 + 0x0d00
    ws.col(2).width = 0x0d00 * 2
    ws.col(3).width = 40 + 0x0d00
    ws.col(4).width = 40 + 0x0d00
    ws.col(5).width = 40 + 0x0d00
    ws.col(6).width = 0x0d00 * 3
    
    _index = 3
    for item in data:
        ws.write(_index, 0, ("%s" % (item['channel'])), text_style)
        ws.write(_index, 1, item['price'], text_style)
        ws.write(_index, 2, item['count'], text_style)
        ws.write(_index, 3, item['costprice'], text_style)
        ws.write(_index, 4, Formula("SUM(C%s*D%s)" % (_index+1, _index+1)), text_style)
        ws.write(_index, 5, 0, text_style)
        ws.write(_index, 6, Formula("SUM(E%s-F%s)" % (_index+1, _index+1)), text_style)
        _index = _index + 1
    
    ws.write(_index, 0, u'合计', text_style)
    ws.write(_index, 1, u'-', text_style)
    ws.write(_index, 2, Formula("SUM(C4:C%s)" % (_index)), text_style)
    ws.write(_index, 3, u'-', text_style)
    ws.write(_index, 4, Formula("SUM(E4:E%s)" % (_index)), text_style)
    ws.write(_index, 5, Formula("SUM(F4:F%s)" % (_index)), text_style)
    ws.write(_index, 6, Formula("SUM(G4:G%s)" % (_index)), text_style)
    ws.write_merge(_index+1, 0, 0, 6, u'开户行： %s' % (bank_name), text_style)
    ws.write_merge(_index+2, 0, 0, 6, u'开户名： %s' % (account_name), text_style)
    ws.write_merge(_index+3, 0, 0, 6, u'帐  号： %s' % (account), text_style)
    print '--------------------save-------------------------'
    print tab_name
    w.save("%s.xls" % tab_name)
    print '--------------------save-------------------------'
    return 'OK'