import random
import urllib2, urllib
import time

def req_url():

    mb = 13635390900
    mb1 = 15815515600
    mb2 = 13527808000
    lkid = 206500001
    url = 'http://127.0.0.1:8802/MR/3/3/'
    #url = 'http://netmad.me/opt/MR/1/8/'
    for i in range(0, 20):
      _mb = random.sample([mb, mb1, mb2], 1)
      values = {'msg' : 'A10',
          'sp' : '1668960',
          #'spnum' : '1668960',
          'mb': '%s' % _mb[0],
          'lkid': '%s' % lkid,
          's': '1'
      }

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
      time.sleep(0.3)

if __name__ == "__main__":
    req_url()
