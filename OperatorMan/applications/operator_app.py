#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from hashlib import md5
from flask import Flask, g
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from OperatorMan.views.base_app import base_view
from OperatorMan.views.channel_app import channel_view
from OperatorMan.views.operator_app import operator_view
from OperatorMan.views.financial_app import financial_view
from OperatorMan.utils.User import User
from OperatorMan.utils.filters import JINJA2_FILTERS, JINJA2_GLOBALS
from OperatorMan.configs import settings
from OperatorCore.models.operator_app import create_operator_session


def create_app(debug=settings.DEBUG):
    app = Flask(__name__, template_folder='../templates/', static_folder="../static")
    app.register_blueprint(base_view)
    app.register_blueprint(operator_view)
    app.register_blueprint(channel_view)
    app.register_blueprint(financial_view)
    app.jinja_env.filters.update(JINJA2_FILTERS)
    app.jinja_env.globals.update(JINJA2_GLOBALS)
    app.secret_key = 'PS#yio`%_!((f_or(%)))s'
    app.debug = debug

    @app.before_request
    def before_request():
        g.session = create_operator_session()

        if current_user.is_authenticated() and not current_user.is_anonymous():
            g.user = current_user

    @app.teardown_request
    def teardown_request(exception):
        g.session.close()

    return app 

app = create_app(settings.DEBUG)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'base_view.login'

@login_manager.user_loader
def load_user(userid):
    user = User()
    if user:
        return user.get_user_id(userid)
    return None

if __name__ == '__main__':
    host = settings.OPERATOR_SERVER_IP #TOWER_MAN_SERVER_IP
    port = settings.OPERATOR_SERVER_PORT #TOWER_MAN_SERVER_PORT
    app.run(host=host, port=port)
