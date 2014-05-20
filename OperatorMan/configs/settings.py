# -*- coding: utf-8 -*-

DEBUG=True

OPERATOR_SERVER_IP = '172.16.10.183'
OPERATOR_SERVER_PORT = 8801

SECRET_KEY = '96e2b3699a852ade9d4d2fd408c93612'

COOKIES_DOMAIN = '172.16.10.183' # cookies 域
HOME_DOMAIN = '172.16.10.183' # 主域

P_LOGIN_URI = '/permission/login/'
P_QUERY_SESSION_URI = '/permission/session/query/'

def P_LOGOUT_URI(session_id):
    return '/permission/logout/%s/' % session_id

def MLOG_QUERY_URI(app_id):
    return '/permission/mlog/query/%s/' % app_id