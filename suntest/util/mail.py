# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
# Filename: mail.py
# Author: huangbin@suntec.net
# Date: 2017.4.14
# Input:
#------------------------------------------------------------------------------
import sys
import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_mail(smtp_config, sender, receivers, subject, message_file):
    """
    Description:
        send mail
    Return: (bool)
    Parameters:
        smtp_config (dict) smtp server config
        sender (str) mail sender
        receivers (str) mail receivers
        subject (str) mail subject
        message_file (str) mail message text content in the file
    """
    smtp_server_host = smtp_config["host"]
    smtp_server_port = smtp_config["port"]
    smtp_login_user = smtp_config["user"]
    smtp_login_pass = smtp_config["port"]

    try:
        with open(message_file, 'rb') as f:
            message = MIMEText(f.read())
    except Exception:
        logging.exception("open message file error.")
        raise

    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receivers

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(smtp_server_host, smtp_server_port)
        smtpObj.login(smtp_login_user, smtp_login_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        return True
    except smtplib.SMTPException:
        logging.exception("send email error.")
        raise
