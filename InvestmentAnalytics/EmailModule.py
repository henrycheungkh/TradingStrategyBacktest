# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 13:45:07 2020

@author: Henry Cheung
"""


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from os.path import basename
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate


def SendEmail(to, subject, HTMLbody, files=None, gmail_user = None, gmail_password = None):
    if gmail_user is None:
        gmail_user = 'xxxxxxxxxxx@gmail.com'
    if gmail_password is None:
        gmail_password = 'xxxxxxxxxxx'
   
        
    sent_from = gmail_user
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sent_from
    message["To"] = ", ".join(to)
    
    text = ""
    html = HTMLbody
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        message.attach(part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, message.as_string())
        server.close()
    
        print ('Email sent!')
    except:
        print ('Something went wrong when emailing...')  
        
# SendEmail(["henry.cheungkh@gmail.com"], 'testing stock', 'AAF.L :')