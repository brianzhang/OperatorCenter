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
from OperatorCore.models.operator_app import SysAdmin, SysAdminLog, SysRole, PubProvince, PubCity, PubBlackPhone, PubMobileArea, \
                create_operator_session, PubProducts, PubBusiType, UsrSPInfo, UsrSPTongLog, UsrCPInfo, UsrCPBank, UsrCPLog, \
                UsrChannel, UsrProvince, UsrCPTongLog, ChaInfo, ChaProvince, DataMo, DataMr, DataEverday, AccountSP, AccountCP, UsrChannelSync, \
                UsrSPSync


from Operator.views import querySPInfo

operator_view = Blueprint('operator_view', __name__)

@operator_view.route('/MO/<int:channel_id>/<SP_ID>/', methods=["GET"])
def channel_mo(channel_id=None, SP_ID=None):
    sp_info = True#querySPInfo(SP_ID)
    if sp_info:
        return jsonify({'ok': True})

    return jsonify({'ok': False, 'SP_ID': SP_ID, 'MSG': 'The SP IS UNDEFINED'})

@operator_view.route('/MR/<int:channel_id>/<SP_ID>/', methods=["GET"])
def channel_mr(channel_id=None,SP_ID=None):
    sp_info = True #querySPInfo(SP_ID)
    if sp_info:
        return jsonify({'ok': True})

    return jsonify({'ok': False, 'SP_ID': SP_ID, 'MSG': 'The SP IS UNDEFINED'})
