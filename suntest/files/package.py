# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: package.py
# Author: huangbin@pset.suntec.net
# Date: 2014.5.14
# Input:
#       src_p: source path
#       tgt_ld: target load name, it can be a file or folder
#       tgt_p: target path
# ------------------------------------------------------------------------------
import os
import logging

import suntest.core.command as Command

logger = logging.getLogger(__name__)


def tar_files(name, path):
    """
    Description:
        compressed files to a package with command tar.
    Return: (bool)
    Parameters:
        name: (str) package name.
        path: (str) target path.
    """
    if not isinstance(name, basestring):
        raise TypeError("name must be a string.")
    if not isinstance(path, basestring):
        raise TypeError("path must be a string.")

    if not os.path.exists(path):
        logger.warning("%s is not exists." % path)
        return False

    tar_file_args = ["tar", "czf", name, path]
    return Command.execute_command(tar_file_args)
