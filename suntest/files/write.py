# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: write.py
# author: huangbin@pset.suntec.net
# date: 2013.12.23
# input:
#       source_path: source path
#       tgt_ld: target load name, it can be a file or folder
#       target_path: target path
# ------------------------------------------------------------------------------
import os
import logging

logger = logging.getLogger(__name__)


def write_file(filepath, content):
    """
    Description:
        write the specify file
    Return: (bool)
    Parameters:
        filepath: (str) file path.
    """
    if not isinstance(filepath, basestring):
        raise TypeError("参数filepath必须是一个字符串类型。")
    if not isinstance(content, basestring):
        raise TypeError("参数content必须是一个字符串类型。")

    if os.path.dirname(filepath) and not os.path.exists(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))

    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    except IOError:
        logger.exception("打开文件失败。")
        return False


def recored_file(filepath, content):
    """
    Description:
        recored the specify file
    Return: (bool)
    Parameters:
        filepath: (str) file path.
    """
    if not isinstance(filepath, basestring):
        raise TypeError("filepath must be a string.")
    if not isinstance(content, basestring):
        raise TypeError("content must be a string.")

    if not os.path.exists(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))

    try:
        with open(filepath, 'a') as f:
            f.write(content)
        return True
    except IOError:
        logger.exception("open file error.")
        return False
