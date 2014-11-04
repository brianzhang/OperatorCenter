import random
import urllib2, urllib
import time

def req_url():

    mb = 13635393900
    mb1 = 15815514800
    mb2 = 13527804700
    lkid = 200005000
    url = 'http://127.0.0.1:8802/MR/3/3/'
    true_count = 0
    error_count = 0
    #url = "http://127.0.0.1:8802/MR/100/1/"
    #url = 'http://netmad.me/opt/MR/1/8/'
    for i in range(0, 100):
      #_mb = random.sample([mb, mb1, mb2], 1)
      #values = {#'msg' : 'A10',
       #   'sp' : '1668960',
          #'spnum' : '1668960',
          #'mb': '%s' % _mb[0],
       #   'lkid': '%s' % lkid,
       #   's': 'OK'
      #}
      values = {'msg' : '10065487',
          spnumber' : '8502',
          'mobile': '%s' % _mb[0],
          'linkid': '%s' % lkid,
          'status': 'OK'
      }
      data = urllib.urlencode(values)


      req = "%s?%s" % (url, data) #urllib2.Request(url, data)
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
          print 'error'
      print '=======info list========'
      print '======Success: %s=======' % true_count
      print '======ERROR: %s=========' % error_count
      print '========================'
      lkid += 1
      time.sleep(0.1)

if __name__ == "__main__":
    req_url()
