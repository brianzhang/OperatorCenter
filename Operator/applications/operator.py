#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except AttributeError:
    pass  #没起作用

from flask import Flask, render_template, request, redirect, url_for, g
from werkzeug import secure_filename

from OperatorCore.models.operator import create_operator_session
from Operator.configs.settings import *
from Operator.views.operator import operator_view

app = Flask(__name__)

def create_app(debug=DEBUG):
    app = Flask(__name__)
    app.register_blueprint(operator_view)
    app.debug = debug

    @app.before_request
    def before_request():
        g.session = create_operator_session()

    @app.teardown_request
    def teardown_request(exception):
        g.session.close()

    return app 

app = create_app(DEBUG) 

if __name__ == "__main__":
    host = OPERATOR_SERVER_IP
    port = OPERATOR_SERVER_PORT
    app.run(host=host, port=port)