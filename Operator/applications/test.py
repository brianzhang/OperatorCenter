import urllib2, urllib


def req_url():

    mb = 13635390980
    lkid = 206500001
    url = 'http://127.0.0.1:8802/MR/3/3/'
    #url = 'http://netmad.me/opt/MR/1/8/'
    for i in range(0, 100):
      values = {'msg' : 'A10',
          'sp' : '1668960',
          #'spnum' : '1668960',
          'mb': '%s' % mb,
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
      lkid += 1

if __name__ == "__main__":
    req_url()
