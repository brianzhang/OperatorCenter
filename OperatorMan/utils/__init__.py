import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from OperatorMan.configs import settings

def send_email(subject=None, to_email=None, content=None):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = settings.SYS_EMAIL
    msg['to'] = to_email
    html = u"""
            <html>
              <head></head>
              <body>
                <h1>Success!</h1>
                <p>%s</p>
              </body>
            </html>
            """ % content

    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    msg.attach(part2)

    s = smtplib.SMTP()
    try:
      s.connect(settings.SMTP_SERVER)
      s.login(settings.SYS_EMAIL, settings.SYS_EMAIL_PASS)
      s.sendmail(settings.SYS_EMAIL, to_email, msg.as_string())
      s.quit()
      print 'send ok'
    except Exception, e:
      print e
