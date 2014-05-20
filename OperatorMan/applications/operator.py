#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, g

from OperatorMan.views.operator import operator_view
from OperatorMan.configs import settings
#from OperatorCore.models.operator import create_tower_session
#from OperatorMan.utils.filters import JINJA2_GLOBALS, JINJA2_FILTERS

def create_app(debug=settings.DEBUG):
    app = Flask(__name__, template_folder='../templates/', static_folder="../static")
    app.register_blueprint(operator_view)
    #app.jinja_env.globals.update(JINJA2_GLOBALS)
    #app.jinja_env.filters.update(JINJA2_FILTERS)
    #app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
    app.secret_key = 'PS#yio`%_!((f_or(%)))s'
    app.debug = debug

    @app.before_request
    def before_request():
        #g.session = create_tower_session()
        print True

    @app.teardown_request
    def teardown_request(exception):
        #g.session.close()
        print True
    return app 

app = create_app(settings.DEBUG)

if __name__ == '__main__':
    host = settings.OPERATOR_SERVER_IP #TOWER_MAN_SERVER_IP
    port = settings.OPERATOR_SERVER_PORT #TOWER_MAN_SERVER_PORT
    app.run(host=host, port=port)
