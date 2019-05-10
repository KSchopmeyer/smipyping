#!/usr/bin/python

import smtplib

TO = 'k.schopmeyer@swbell.net'
SUBJECT = 'TEST MAIL'
TEXT = 'Here is a message from python.'

# exchange Sign In
exchange_sender = 'smipyping@snia.org'
exchange_user = 'EXCHPROD\\01074002'
exchange_passwd = 'Pa$$w0rd'
SMTP_SERVER = 'exchange.postoffice.net'
USE_TLS = True

if USE_TLS:
    SMTP_PORT = 587
else:
    SMTP_PORT = 25


server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
server.set_debuglevel(1)
server.ehlo()
if USE_TLS:
    server.starttls()
    server.ehlo()

server.login(exchange_user, exchange_passwd)

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
