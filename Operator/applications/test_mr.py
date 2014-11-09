import random
import urllib2, urllib
import time

def req_url():

    mb   = 15915420000
    mb1 = 18823370000
    mb2 = 15019200000
    mb3 = 15815810000
    mb4 = 18211010000
    mb5 = 13006660000
    mb6 = 13166850000
    lkid = 226000000
    #url = 'http://127.0.0.1:8802/MR/3/3/'
    true_count = 0
    error_count = 0
    url = "http://127.0.0.1:8802/MR/100/1/"
    #url = 'http://netmad.me/opt/MR/1/8/'
    for i in range(0, 10000):
      _mb = random.sample([mb, mb2, mb3, mb6], 1)
      values = {'msg' : '10065487',
          'spnumber' : '8502',
          'mobile': '%s' % _mb[0],
          'linkid': '%s' % lkid,
          'status': 'OK'
      }
      data = urllib.urlencode(values)
      req = "%s?%s" % (url, data) 
      print "URL: %s " % req
      try:
          response = urllib.urlopen(req)
          data = response.read()
          print 'DATA: %s' % data
          if data == 'OK':
              true_count += 1
          else:
              error_count += 1
      except Exception, e:
          error_count += 1
      lkid += 1
      mb += 1
      #mb1 += 1
      mb2 += 1
      mb3 += 1
      #mb5 += 1
      mb6 += 1
      time.sleep(0.1)
    print '=======info list========'
    print '======Success: %s=======' % true_count
    print '======ERROR: %s=========' % error_count
    print '========================'

if __name__ == "__main__":
    req_url()
