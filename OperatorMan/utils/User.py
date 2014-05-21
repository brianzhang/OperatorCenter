# -*- coding: utf-8 -*-
import os

import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUserMixin,
                            confirm_login, fresh_login_required)
from flask import g

from OperatorCore.models.operator import SysAdmin, create_operator_session


class User(UserMixin):
    def __init__(self, userpwd=None, active=True, id=None, username=None, realname=None, role_id=None, phone=None, qq=None, email=None, is_show=True, content='', create_time=datetime.datetime.now()):

        self.email = email
        self.username = username
        self.userpwd = userpwd
        self.is_show = is_show
        self.isAdmin = False
        self.id = None


    def save(self): 
        new_user = SysAdmin()
        new_user.username = self.username
        new_user.userpwd = self.userpwd
        new_user.realname = self.realname
        new_user.role_id = self.role_id
        new_user.phone = self.phone
        new_user.qq = self.qq
        new_user.email = self.email
        new_user.is_show = self.is_show
        new_user.content = self.content
        new_user.create_time = self.create_time

        
        try:
            g.session.add(new_user)
            g.session.commit()
            return new_user.id

        except Exception, e:

            g.session.rollback()

            return False

    def get_user(self, username, userpwd):

        try:
            dbUser = g.session.query(SysAdmin).filter(SysAdmin.username==username).\
                filter(SysAdmin.userpwd==userpwd).\
                filter(SysAdmin.is_show==True).first()

            if dbUser:
                self.email = dbUser.email
                self.userpwd = dbUser.userpwd
                self.realname = dbUser.realname
                self.id = dbUser.id
                return self
            else:
                return None
        except:
            print "there was an error"
            return None

    def get_user_id(self, id):

        try:
            dbUser = g.session.query(SysAdmin).filter(SysAdmin.id==id).first()

            if dbUser:
                self.email = dbUser.email
                self.userpwd = dbUser.userpwd
                self.realname = dbUser.realname
                self.id = dbUser.id
                return self
            else:
                return None
        except:
            print "there was an error"
            return None            
    
    def get_by_email_w_password(self, email):

        try:
            dbUser = g.session.query(SysAdmin).filter(SysAdmin.email==email).first()
            if dbUser:
                self.email = dbUser.email
                self.userpwd = dbUser.userpwd
                self.id = dbUser.id
                return self
            else:
                return None
        except:
            print "there was an error"
            return None

class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"