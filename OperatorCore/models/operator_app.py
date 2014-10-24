# -*- coding: utf-8 -*-

import time
import datetime
import sys
#sys.path.append("..")  #windows paths settings.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, BigInteger, Integer, Boolean, Float, Numeric,
                        String, DateTime, ForeignKey, create_engine, Float,
                        UniqueConstraint, event, and_)
from sqlalchemy.orm import sessionmaker, relationship
from OperatorCore.configs import settings


operator_engine = create_engine('%s?charset=utf8' % settings.DB_SPOTLIGHT_URI, encoding='utf-8',
                             convert_unicode=True, pool_size=settings.DB_POOL_SIZE,
                             pool_recycle=settings.DB_POOL_RECYCLE_TIMEOUT, echo=settings.DB_DEBUG)

OperatorBase = declarative_base(bind=operator_engine)

class SysRole(OperatorBase):
    __tablename__ = 'sys_role'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    rolename = Column(String(20), unique=True, nullable=False)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    rights = Column(String(100), nullable=False)

class SysAdmin(OperatorBase):
    __tablename__ = 'sys_admin'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id  = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    userpwd = Column(String(50), nullable=False)
    realname = Column(String(50), nullable=False)
    role_id = Column(Integer, ForeignKey('sys_role.id'))
    phone = Column(String(11), nullable=False)
    qq = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

    def __init__(self, username=None,
                    userpwd=None,
                    realname=None,
                    role_id=None,
                    phone=None,
                    qq=None,
                    email=None,
                    is_show=None,
                    content=None,
                    create_time=None):

        self.username = username
        self.userpwd = userpwd
        self.realname = realname
        self.role_id = role_id
        self.phone = phone
        self.qq = qq
        self.email = email
        self.is_show = is_show
        self.content = content
        self.create_time = create_time

    def __repr__(self):
        return '<SysAdmin %s>' % self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

class SysAdminLog(OperatorBase):
    __tablename__ = 'sys_adminlog'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id  = Column(Integer, primary_key=True)
    adminid = Column(Integer, ForeignKey('sys_admin.id'))
    op_type = Column(Integer, nullable=False)
    op_title = Column(String(200), nullable=False)
    op_content = Column(String(1000), nullable=False)
    create_time = Column(DateTime, nullable=False)

    admin = relationship("SysAdmin")

class SysRights(OperatorBase):
    __tablename__ = 'sys_rights'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    rightname = Column(String(50), nullable=False)
    is_show = Column(Boolean, nullable=False)
    create_time = Column(DateTime, nullable=False)

class PubProvince(OperatorBase):
    """docstring for PubProvince"""
    __tablename__ = 'pub_province'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    province = Column(String(50), nullable=False)
    create_time = Column(DateTime, nullable=False)

    def __init__(self, arg):
        super(PubProvince, self).__init__()
        self.arg = arg

class PubCity(OperatorBase):

    """docstring for PubCity"""
    __tablename__ = 'pub_city'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    province = Column(Integer, ForeignKey('pub_province.id'))
    city = Column(String(50), nullable=False)
    create_time = Column(DateTime, nullable=False)

class PubBlackPhone(OperatorBase):

    """docstring for PubBlackPhone"""
    __tablename__ = 'pub_blackphone'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    mobile = Column(String(11), nullable=False)
    province = Column(Integer, ForeignKey('pub_province.id'))
    city = Column(Integer, ForeignKey('pub_city.id'))
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)
    city_info = relationship("PubCity")
    province_info = relationship("PubProvince")

class PubMobileArea(OperatorBase):

    """docstring for PubMobileArea"""
    __tablename__ = 'pub_mobilearea'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    mobile = Column(String(11), nullable=False)
    province = Column(Integer, ForeignKey('pub_province.id'))
    city = Column(Integer, ForeignKey('pub_city.id'))
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

class PubProducts(OperatorBase):

    """docstring for PubProducts"""
    __tablename__ = 'pub_products'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    proname = Column(String(50), nullable=False)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

class PubBusiType(OperatorBase):

    """docstring for PubBusiType"""
    __tablename__ = 'pub_busitype'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    is_show = Column(Boolean, nullable=False)
    create_time = Column(DateTime, nullable=False)

class UsrSPInfo(OperatorBase):

    """docstring for UsrSPInfo"""
    __tablename__ = 'usr_spinfo'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    adminid = Column(Integer, ForeignKey('sys_admin.id'))
    link_name = Column(String(50), nullable=False)
    link_phone = Column(String(50), nullable=False)
    link_qq = Column(String(50), nullable=False)
    link_email = Column(String(50), nullable=False)
    link_address = Column(String(50), nullable=False)
    startdate = Column(DateTime, nullable=False)
    enddate = Column(DateTime, nullable=False)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

class UsrCPInfo(OperatorBase):

    """docstring for UsrCPInfo"""
    __tablename__ = 'usr_cpinfo'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    loginname = Column(String(50), nullable=False)
    loginpwd = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    adminid = Column(Integer, ForeignKey('sys_admin.id'))
    link_name = Column(String(50), nullable=False)
    link_phone = Column(String(50), nullable=False)
    link_qq = Column(String(50), nullable=False)
    link_email = Column(String(50), nullable=False)
    link_address = Column(String(50), nullable=False)
    startdate = Column(DateTime, nullable=False)
    enddate = Column(DateTime, nullable=False)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

    admin_info = relationship("SysAdmin")
    bank_info = relationship("UsrCPBank")

class UsrCPBank(OperatorBase):

    """docstring for UsrCPBank"""
    __tablename__ = 'usr_cpbank'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    bankname =  Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    bankcard = Column(String(50), nullable=False)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

class UsrCPLog(OperatorBase):

    """docstring for UsrCPLog"""
    __tablename__ = 'usr_cplog'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    adminid = Column(Integer, ForeignKey('sys_admin.id'))
    title = Column(String(100), nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

class UsrProvince(OperatorBase):

    """docstring for UsrProvince"""
    __tablename__ = 'usr_province'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    channelid = Column(Integer, ForeignKey('usr_channel.id'))
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    adminid = Column(Integer, ForeignKey('sys_admin.id'))
    province = Column(Integer, ForeignKey('pub_province.id'))
    city =  Column(String(200), nullable=False)
    daymax = Column(Integer)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

    province_info = relationship("PubProvince")

class ChaProvince(OperatorBase):

    """docstring for ChaProvince"""
    __tablename__ = 'cha_province'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    province = Column(Integer, ForeignKey('pub_province.id'))
    city = Column(String(200), nullable=False)
    daymax = Column(Integer)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(200), nullable=False)
    create_time = Column(DateTime, nullable=False)
    province_info = relationship(PubProvince)

class ChaInfo(OperatorBase):

    """docstring for ChaInfo"""
    __tablename__ = 'cha_info'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    cha_name = Column(String(50), nullable=False)
    spid = Column(Integer, ForeignKey('usr_spinfo.id'))
    proid = Column(Integer, ForeignKey('pub_products.id'))
    busi_type = Column(Integer, ForeignKey('pub_busitype.id'))
    operator = Column(String(20), nullable=False)
    sx = Column(String(150), nullable=False)
    spnumber = Column(String(20), nullable=False)
    sx_type = Column(Integer)
    price = Column(Integer)
    costprice = Column(Integer)
    fcpric = Column(Integer)
    bl = Column(Integer)
    daymax = Column(Integer)
    monmax = Column(Integer)
    is_show = Column(Boolean, nullable=False)
    remark = Column(String(2000), nullable=False)
    content = Column(String(200), nullable=False)
    create_time = Column(DateTime, nullable=False)

    sp_info = relationship(UsrSPInfo)
    product_info = relationship(PubProducts)
    busi_info = relationship(PubBusiType)
    cha_province = relationship(ChaProvince)

class UsrChannel(OperatorBase):

    """docstring for UsrChannel"""
    __tablename__ = 'usr_channel'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id  = Column(Integer, primary_key=True)
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    adminid = Column(Integer, ForeignKey('sys_admin.id'))
    momsg = Column(String(150), nullable=False)
    sx_type = Column(Integer)
    spnumber = Column(String(20), nullable=False)
    fcprice = Column(Integer)
    bl = Column(Integer)
    backurl = Column(String(100), nullable=False)
    is_show = Column(Boolean, nullable=False)
    content = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

    cha_info = relationship(ChaInfo)
    cp_info = relationship(UsrCPInfo)
    user_info = relationship(SysAdmin)
    usr_province = relationship(UsrProvince)

class UsrChannelSync(OperatorBase):

    """docstring for UsrChannelSync"""
    __tablename__ = 'usr_channel_sync'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    sync_type = Column(Integer)
    status_key =  Column(String(100), nullable=False)
    url = Column(String(100), nullable=False)
    is_rsync = Column(Boolean, nullable=False)
    is_show  = Column(Boolean, nullable=False)
    spnumber = Column(String(100), nullable=False)
    mobile = Column(String(100), nullable=False)
    linkid = Column(String(100), nullable=False)
    msg = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

    cha_info = relationship(ChaInfo)

class UsrSPSync(OperatorBase):
    """docstring for UsrSPSync"""
    __tablename__ = 'usr_sp_sync'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    spid = Column(Integer, ForeignKey('usr_spinfo.id'))
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    sync_type = Column(Integer)
    status_key =  Column(String(100), nullable=False)
    url = Column(String(100), nullable=False)
    is_rsync = Column(Boolean, nullable=False)
    is_show  = Column(Boolean, nullable=False)
    spnumber = Column(String(100), nullable=False)
    mobile = Column(String(100), nullable=False)
    linkid = Column(String(100), nullable=False)
    msg = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)

    usr_spinfo = relationship(UsrSPInfo)
    cha_info = relationship(ChaInfo)

class UsrCPTongLog(OperatorBase):

    """docstring for UsrCPTongLog"""
    __tablename__ = 'usr_cptonglog'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    urltype = Column(Integer)
    mobile = Column(String(15), nullable=False)
    spnumber = Column(String(20), nullable=False)
    momsg = Column(String(150), nullable=False)
    linkid = Column(String(50), nullable=False)
    tongurl = Column(String(200), nullable=False)
    backmsg = Column(String(50), nullable=False)
    tongdate = Column(Integer)
    create_time = Column(DateTime, nullable=False)
    cp_info = relationship(UsrCPInfo)
    channe_info = relationship(ChaInfo)

class UsrSPTongLog(OperatorBase):

    """docstring for UsrSPTongLog"""
    __tablename__ = 'usr_sptonglog'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    spid = Column(Integer, ForeignKey('usr_spinfo.id'))
    urltype = Column(Integer, nullable=False)
    mobile = Column(String(11), nullable=False)
    spnumber = Column(String(15), nullable=False)
    momsg = Column(String(150), nullable=False)
    linkid = Column(String(50), nullable=False)
    tongurl = Column(String(200), nullable=False)
    is_show = Column(Boolean, nullable=False)
    tongdate = Column(Integer, nullable=False)
    create_time = Column(DateTime, nullable=False)
    sp_info = relationship(UsrSPInfo)
    channe_info = relationship(ChaInfo)

class DataMo(OperatorBase):

    """docstring for DataMo"""
    __tablename__ = 'data_mo'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    mobile = Column(String(15), nullable=False)
    momsg = Column(String(50), nullable=False)
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    spnumber = Column(String(20), nullable=False)
    price = Column(Integer)
    linkid = Column(String(20), nullable=False)
    province = Column(Integer, ForeignKey('pub_province.id'))
    city = Column(Integer, ForeignKey('pub_city.id'))
    regdate = Column(Integer)
    reghour = Column(Integer)
    create_time = Column(DateTime, nullable=False)

    cp_info = relationship(UsrCPInfo)
    channe_info = relationship(ChaInfo)
    provinces = relationship(PubProvince)
    citys = relationship(PubCity)

class DataMr(OperatorBase):

    """docstring for DataMr"""
    __tablename__ = 'data_mr'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    mobile = Column(String(15), nullable=False)
    momsg = Column(String(50), nullable=False)
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    spnumber = Column(String(20), nullable=False)
    price = Column(Float(), default=0.0)
    linkid = Column(String(20), nullable=False)
    province = Column(Integer, ForeignKey('pub_province.id'))
    city = Column(Integer, ForeignKey('pub_city.id'))
    state = Column(Boolean, nullable=False)
    is_kill = Column(Boolean, nullable=False)
    regdate = Column(Integer)
    reghour = Column(Integer)
    create_time = Column(DateTime, nullable=False)

    cp_info = relationship(UsrCPInfo)
    channe_info = relationship(ChaInfo)
    provinces = relationship(PubProvince)
    citys = relationship(PubCity)

class DataEverday(OperatorBase):

    """docstring for DataEverday"""
    __tablename__ = 'data_everday'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    province = Column(Integer, ForeignKey('pub_province.id'))
    city = Column(Integer, ForeignKey('pub_city.id'))
    price = Column(Float(), default=0.0)
    mo_all = Column(Integer)
    mr_all = Column(Integer)
    mr_cp = Column(Integer)
    tj_hour = Column(Integer)
    tj_date = Column(Integer)
    create_time = Column(DateTime, nullable=False)
    sp_info = relationship(UsrCPInfo)
    channe_info = relationship(ChaInfo)
    city_info = relationship(PubCity)
    province_info = relationship(PubProvince)

class AccountSP(OperatorBase):

    """docstring for AccountSP"""
    __tablename__ = 'account_sp'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    spid = Column(Integer, ForeignKey('usr_spinfo.id'))
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    count = Column(Integer)
    price = Column(Float(), default=0.0)
    costprice = Column(Float(), default=0.0)
    totalprice = Column(Float(), default=0.0)
    js_state = Column(Boolean, nullable=False)
    js_date = Column(Integer)
    create_time = Column(DateTime, nullable=False)

    sp_info = relationship(UsrSPInfo)
    channe_info = relationship(ChaInfo)

class AccountCP(OperatorBase):

    """docstring for AccountCP"""
    __tablename__ = 'account_cp'
    __table_args__ = ({'mysql_engine': 'InnoDB'}, )

    id = Column(Integer, primary_key=True)
    cpid = Column(Integer, ForeignKey('usr_cpinfo.id'))
    channelid = Column(Integer, ForeignKey('cha_info.id'))
    count = Column(Integer)
    price = Column(Float(), default=0.0)
    fcprice = Column(Float(), default=0.0)
    totalprice = Column(Float(), default=0.0)
    js_state = Column(Boolean, nullable=False)
    js_date = Column(Integer)
    create_time = Column(DateTime, nullable=False)

    cp_info = relationship(UsrCPInfo)
    channe_info = relationship(ChaInfo)

_Session = sessionmaker(bind=operator_engine, expire_on_commit=False)

def create_operator_session():
    return _Session()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    if sys.argv[1] == 'create':
        OperatorBase.metadata.create_all()
    elif sys.argv[1] == 'drop':
        OperatorBase.metadata.drop_all()
