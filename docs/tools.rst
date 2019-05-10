.. _`Tools`:

Tools
============

.. _`Overview`:


Overview
--------
The basic functionality for smipyping is contained in the single `smicli`
executable.  However, we have included a number of other tools to help with
specific tasks.

.. _`Email tool`:


Email tool
----------

The tools directory contains a separate Python tool to send email (pysendmail)
which acts similar to the system sendmail in that it can be used to send
email to outside SMTP servers.  This is a command line tool and the
usage documentation can be viewed by executing `pysendmail -h`.

By using this tool, avoids the effort to activate tools like sendmail for the
environment containing smipyping.

Generally it allows the user to send mail to external SMTP servers that contain
messages base on text or html files.  It is used by smipyping to send
reports for activities like the weekly report, etc. that are driven by
schedulers like crontab.

The input parameters include:

1. The to address

2. The From Addresses

3. The Subject Line

4. Optional CC addresses

5. The file containing the text or html content.

6. The name of the email configuration file. The default is 'email.ini' in the
execution directory.

A separate config file must be defined to use this tool to define the
characteristics of the SMTP server to be used. This allows defining the
SMTP server, user, passwords, without having this information committed to the
smipping source code.

The configuration file is a standard ini format that contains name/value pairs
for the required fields.  The following is an example of this file::

    # Configuration file for pysendmail tool of smipyping.  This keeps all of
    # issues concerning email security out of the software release.  This file
    # should NOT be part of the collection in github to avoid making the
    # email password public.
    [email]
    #
    #  A default email user name that is used if the from address is not
    #  provided on the command line. This line is optional.
    #
    DefaultFromAddress=<single from address>
    #
    # email user account name. This line is required.
    #
    user=<The email user name>
    #
    # email user account password. This line is required.
    #
    password=<password>
    # email server NOTE: For the moment, pysendmail assumes that tls is enabled
    # for the server.  This line is optional.  The default is
    # `smtp.gmail.com:587`.
    SmtpServer=smtp.gmail.com:587

This tool has been tested specifically with gmail as the SMTP server and using
tls.

To set it up for gmail with an installed smipyping:

1. Get a gmail account so that the user name and password are available.

2. Set up the email.ini configuration file.

3. Test by entering the following:

    pysendmail -t <to email> -f <from email> -s "subject test" -F <file to sent> -v

This will try to create the email and send it.  the -v option will show the
interaction between pysendmail and the SMTP server.
