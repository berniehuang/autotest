# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: read.py
# author: huangbin@pset.suntec.net
# date: 2013.12.23
# input:
#       none
# ------------------------------------------------------------------------------
import os
import logging

logger = logging.getLogger(__name__)


def read_file(filepath):
    """
    Description:
        read the specify file
    Return: (bool)
    Parameters:
        filepath: (str) file path.
    """
    if not isinstance(filepath, basestring):
        raise TypeError("文件路径类型必须是字符串。")

    if not os.path.exists(filepath):
        logger.error("文件路径%s不存在。" % filepath)
        return False

    try:
        with open(filepath, 'r') as f:
            content = f.readlines()
            return content
    except IOError:
        logger.exception("打开文件失败。")
        return False


def display_file(filepath, title=''):
    """
    Description:
        print the specify file content in stdout.
    Return: (bool)
    Parameters:
        filepath: (str) file path.
        title: (str) the title stdout.
    """
    if not isinstance(filepath, basestring):
        raise TypeError("文件路径类型必须是字符串。")

    if not os.path.exists(filepath):
        logger.error("文件路径%s不存在。" % filepath)
        return False

    print "=" * 110
    print '                                              --%s--' % title
    try:
        with open(filepath, 'r') as f:
            print "%s\n" % f.read()
    except IOError:
        logger.error("打开文件失败。")
        return False
    print "=" * 110

    return True
