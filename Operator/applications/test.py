import random
import urllib2, urllib
import time

def req_url():

    mb = 13728922000
    mb1 = 15914107000
    mb2 = 15099923000
    lkid = 200210000
    url = 'http://127.0.0.1:8802/MR/3/3/'
    #url = "http://127.0.0.1:8802/MO/100/1/"
    #url = 'http://netmad.me/opt/MR/1/8/'
    for i in range(0, 200):
      _mb = random.sample([mb, mb1, mb2], 1)
      values = {'msg' : '860',
          'sp' : '19008666',
          'spnum' : '19008666',
          'mb': '%s' % _mb[0],
          'lkid': '%s' % lkid,
          's': 'OK'
      }
      #values = {'msg' : '10065487',
      #    'spnumber' : '8502',
      #    'mobile': '%s' % _mb[0],
      #    'linkid': '%s' % lkid,
      #    'status': 'OK'
      #}
      data = urllib.urlencode(values)


      req = "%s?%s" % (url, data) #urllib2.Request(url, data)
      print "URL: %s " % req
      try:
          response = urllib.urlopen(req)
          data = response.read()
          print 'DATA: %s' % data
          if data == 'OK':
              print 'True'
          else:
              print 'False'
      except Exception, e:
          print e
          print 'error'
      mb += 1
      mb1 += 1
      mb2 += 1
      lkid += 1
      time.sleep(0.2)

if __name__ == "__main__":
    req_url()
