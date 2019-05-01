#!/usr/bin/python

import smtplib

TO = 'k.schopmeyer@swbell.net'
SUBJECT = 'TEST MAIL'
TEXT = 'Here is a message from python.'

# exchange Sign In
exchange_sender = 'smipyping@snia.org'
exchange_passwd = 'Pa$$w0rd'

server = smtplib.SMTP('smtp.exchange.postoffice.net', 587)
server.set_debuglevel(1)
server.ehlo()
server.starttls()
server.login(exchange_sender, exchange_passwd)

BODY = '\r\n'.join(['To: %s' % TO,
                    'From: %s' % exchange_sender,
                    'Subject: %s' % SUBJECT,
                    '', TEXT])

try:
    server.sendmail(exchange_sender, [TO], BODY)
    print ('email sent')
except:
    print ('error sending mail')

server.quit()
