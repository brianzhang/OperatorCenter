import random
import urllib2, urllib
import time

def req_url():

    mb   = 13464000000
    mb1 = 13464560000
    mb2 = 13503600000
    mb3 = 13503650000
    mb4 = 13482190000
    mb5 = 13482260000
    mb6 = 13470860000
    mb7 = 13400810000
    mb8 = 13406190000
    mb9 = 13409390000
    lkid = 402939929392991
    #url = 'http://127.0.0.1:8802/MR/3/3/'
    true_count = 0
    error_count = 0
    url = "http://127.0.0.1:8802/mr/100/"
    #url = 'http://netmad.me/opt/MR/1/8/'
    for i in range(0, 1000000):
      _mb = random.sample([mb, mb1, mb2, mb3, mb4, mb5, mb6, mb7, mb8, mb9], 1)
      values = {'msg' : 'cwems444:44:d',
          'spnumber' : '1065889919',
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
      mb1 += 1
      mb2 += 1
      mb3 += 1
      mb5 += 1
      mb6 += 1
      mb7 += 1
      mb8 += 1
      mb9 += 1
      time.sleep(0.1)
    print '=======info list========'
    print '======Success: %s=======' % true_count
    print '======ERROR: %s=========' % error_count
    print '========================'

if __name__ == "__main__":
    req_url()
