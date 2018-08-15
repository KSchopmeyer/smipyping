# (C) Copyright 2017 Inova Development Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Class to send mail through a defined SMTP Server
"""
from __future__ import print_function

import email.message
import smtplib
SMTP_SERVER = 'smtp.gmail.com:587'


class SendMail(object):
    """Python send mail package
    """
    def __init__(self, account_username, account_pw, smtp_server=None,
                 verbose=None):
        """
        Set the initialization variables for sending the email through a
        defined account and user name. This also logs into the server.

        Parameters:

          account_username (:term:`string`):
            Defines the account user name for the smtp server

          account_pw (:term:`string`):
            Defines the account password for the smtp server

          smtp_server  (:term:`string`):
            Optional string that defines the smtp server address. Generally
            in the forms 'smtp.<host name>:<port>

        Raises:
          SMTPException: If the server connection setup or login fail
        """
        self.verbose = verbose
        if not smtp_server:
            self.smtp_server = SMTP_SERVER
        try:
            self.server = smtplib.SMTP(SMTP_SERVER)
            if verbose:
                self.server.set_debuglevel(1)
            self.server.ehlo()
            self.server.starttls()
            self.server.login(account_username, account_pw)
        except smtplib.SMTPException as se:
            print('SMTP connection Exception error $s mail not sent' % se)
            raise se

    def send_mail(self, fromaddr, toaddrs, subject=None, payload=None,
                  payload_type=None, cc_addresses=None):
        """
        Try to send the message using the python smtplib. This always sends
        through tls.

        Parameters:

          from_addr  (:term:`string`):
            The from address for the mail.  Must be a complete email address

          from_addrs  (list of :term:`string` or :term:`string`):
            The to addresses for the mail. May be either a single email address
            or multiple addresses within a python list

          subject  (:term:`string`):
            Optional subject for the email as a single string

          payload (:term:`string`):
            Optional payload for email message

          payload_type: (:term:`string`):
            Optional defines a type for the payload.  The options are
            'text' and 'html'.


        """
        mail_msg = email.message.Message()
        mail_msg['From'] = '"%s"' % fromaddr

        mail_msg['To'] = ', '.join(toaddrs)
        # if cc_addresses:
        #    mail_msg['CC'] = cc_addresses
        if subject:
            mail_msg['Subject'] = subject
        if payload:
            mail_msg.set_payload(payload)

        if payload_type == 'html':
            mail_msg.add_header('Content-Type', 'text/html')

        if self.verbose:
            print('sendmail \n  from %s, \n  to %s, \nmsg %s' %
                  (mail_msg['From'], mail_msg['To'], mail_msg.as_string()))
        try:
            rslt = self.server.sendmail(fromaddr,
                                        toaddrs,
                                        mail_msg.as_string())

            print('Msg sent from %s to %s' % (fromaddr, toaddrs))
            if rslt:
                print('Refused recipients: %s' % rslt)

        except Exception as ex:
            print('SEND msg from %s to %s\n failed with exception %s' %
                  (mail_msg['From'], mail_msg['To'], ex))
            raise ex
