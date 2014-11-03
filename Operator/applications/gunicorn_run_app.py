#coding=utf-8
import logging
from Operator.configs import settings



bind =  "%s:%s" % (settings.OPERATOR_SERVER_IP, settings.OPERATOR_SERVER_PORT)
workers = 4
worker_connections = 100
worker_class = "gevent"
#worker_class = "sync"
backlog = 2048
debug = settings.SYS_DEBUG
log_level = logging.ERROR
daemon = True
pidfile = "/root/logs/operator.pid"
logfile =  "/root/logs/operator.log"
#max_requests = 10000
