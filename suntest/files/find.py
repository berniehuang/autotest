# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: find.py
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


def find_file_path(target_path, target_file):
    """
    Description:
        find target file in target path and get file path.
    Return: (str) file path
    Parameters:
        target_path: (str) target path.
        target_file: (str) target file.
    """
    for file_name in os.listdir(target_path):
        file_path = os.path.join(target_path, file_name)
        if os.path.isfile(file_path):
            if target_file == file_name:
               return file_path
        elif os.path.isdir(file_path):
            sub_file_path = find_file_path(file_path, target_file)
            if sub_file_path:
                return sub_file_path

    return str()
