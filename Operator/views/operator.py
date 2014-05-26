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
from Operator.configs import settings
from OperatorCore.models.operator import SysAdmin, SysAdminLog, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UserSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP

from Operator.views import querySPInfo

operator_view = Blueprint('operator_view', __name__)

@operator_view.route('/channel/<SP_ID>/MO/', methods=["GET"])
def channel_mo(SP_ID=None):
    sp_info = querySPInfo(SP_ID)
    if sp_info:
        return jsonify({'ok': True, 'sp_info': {'id': sp_info.id, 'name': sp_info.name}})    

    return jsonify({'ok': False, 'SP_ID': SP_ID, 'MSG': 'The SP IS UNDEFINED'})

@operator_view.route('/channel/<SP_ID>/MR/', methods=["GET"])
def channel_mr(SP_ID=None):
    sp_info = querySPInfo(SP_ID)
    if sp_info:
        return jsonify({'ok': True, 'sp_info': {'id': sp_info.id, 'name': sp_info.name}})    

    return jsonify({'ok': False, 'SP_ID': SP_ID, 'MSG': 'The SP IS UNDEFINED'})