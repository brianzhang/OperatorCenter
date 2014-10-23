#OperatorCenter

=========

#Config

#Flask-WTF
```
https://flask-wtf.readthedocs.org/en/latest/install.html
```
#Flask-WTF
```
$ easy_install Flask-WTF
```

#simplejson
```
https://pypi.python.org/pypi/simplejson/
```

#Flask-Login

```
$ easy_install Flask-Login
```
# MySql-Python

```
$ easy_install mysql-python
```
#Windows PYTHON_PATH SET

# 在我的电脑中设置：

```
PYTHONPATH: G:/workspace/OperaorCenter/

http://yuji.wordpress.com/2009/08/31/python-on-windows-setting-pythonpath-environment-variable/
```

# SQLAlchemy 模块依赖

```
URL https://pypi.python.org/pypi/SQLAlchemy/0.9.8
Download: https://pypi.python.org/packages/source/S/SQLAlchemy/SQLAlchemy-0.9.8.tar.gz
```
# MYSQLDB for windows:
```
http://www.codegood.com/archives/129
```

# 业务逻辑

```
1、 查询该手机号码是否为黑名单
2、 查询该号码的归属地（省份、地市）
3、 查询该号码对应的linkid，在表中是否已经存在（linkid 在表中具有唯一性）
4、 查询该号码当天、对应channelid的总条数；当月对应channelid的总条数
5、 查询该数据归属的cpid
6、 查询该数据对应cpid，特定省份当天的总条数（判断是否超限制）
7、 查询该数据是否扣量（根据预先设置的扣量比例来判断）

```
