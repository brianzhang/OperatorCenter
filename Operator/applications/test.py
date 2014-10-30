import urllib2, urllib


def req_url():

    mb = 15815517000
    lkid = 206200001
    url = 'http://127.0.0.1:8802/MR/3/3/'
    #url = 'http://netmad.me/opt/MR/1/8/'
    for i in range(0, 100):
      values = {'msg' : 'A10',
          'sp' : '1668960',
          'mb': '%s' % mb,
          'lkid': '%s' % lkid,
          's': '1'
      }

      data = urllib.urlencode(values)

      print "Req data %s" % data
      req = "%s?%s" % (url, data) #urllib2.Request(url, data)
      print "Req URL: %s " % req
      try:
          response = urllib.urlopen(req)
          data = response.read()
          print 'Return Data: %s' % data
          if data == 'OK':
              print 'True'
          else:
              print 'False'
      except Exception, e:
          print e
          print 'error'
      mb += 1
      lkid += 1

if __name__ == "__main__":
    req_url()
