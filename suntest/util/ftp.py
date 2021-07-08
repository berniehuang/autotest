#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: ftp.py
# author: huangbin@pset.suntec.net
# date: 2014.6.17
# input:
#       src_p: file path will be committed
# ------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# from ftplib import FTP
import ftplib
import os
import logging

logger = logging.getLogger(__name__)


class FTP(object):
    def __init__(self):
        self.ftp = ftplib.FTP()
        self.bufsize = 1024

    def connect(self, ip_address, port, timeout=30):
        try:
            self.ftp.connect(ip_address.encode('gbk'), port.encode('gbk'), timeout)
            return True
        except:
            logger.error("ip address: %s port: %s unreachable." % (ip_address, port))
            return False

    def login(self, username, password):
        try:
            self.ftp.login(username, password)
            logger.info(self.ftp.getwelcome())
            return True
        except:
            logger.error("ftp login failure.")
            self.ftp.quit()
            return False

    def upload(self, upload_dir, upload_list):
        try:
            self.ftp.cwd(upload_dir)
        except:
            logger.error(upload_dir + " unreachable, return false")
            self.disconnect()
            return False

        for pushfile in upload_list.split(' '):
            with open(pushfile, 'rb') as f:
                try:
                    self.ftp.storbinary('STOR %s' % os.path.basename(pushfile), f, self.bufsize)
                except ftplib.logger.error_perm:
                    logger.error("file " + pushfile + " push failed, will loop next")
                    continue
                self.ftp.set_debuglevel(0)
                logger.info("ftp  up " + pushfile +" OK")
                f.close()

        logger.info("function upload() finished")
        self.disconnect()

        return True

    def download(self, download_dir, download_list=[]):
        try:
            self.ftp.cwd(download_dir)
        except:
            logger.error(download_dir + " unreachable, return false")
            self.disconnect()
            return False

        if len(download_list) == 1 and download_list[0] is '*':
            filelist = self.ftp.nlst()
            for downloadfile in filelist:
                logger.info("downloadfile is " + downloadfile)

                with open(downloadfile, 'wb') as f:
                    try:
                        self.ftp.retrbinary(u'RETR %s' % os.path.basename(downloadfile), f.write, self.bufsize)
                    except ftplib.logger.error_perm:
                        logger.error("file " + downloadfile + " ftp get failed, will loop next")
                        continue
                    self.ftp.set_debuglevel(0)
                    logger.info("ftp  download " + downloadfile + " OK")
                    f.close()
        else:
            for downloadfile in download_list:
                logger.info("downloadfile is " + downloadfile)

                with open(downloadfile, 'wb') as f:
                    try:
                        self.ftp.retrbinary(u'RETR %s' % os.path.basename(downloadfile), f.write, self.bufsize)
                    except ftplib.logger.error_perm:
                        logger.error("file " + downloadfile + " ftp get failed, will loop next")
                        continue
                    self.ftp.set_debuglevel(0)
                    logger.info("ftp  download " + downloadfile + " OK")
                    f.close()

        self.disconnect()
        return True

    def disconnect(self):
        self.ftp.quit()
        return True
