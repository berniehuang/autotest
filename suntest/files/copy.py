# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: copy.py
# author: huangbin@pset.suntec.net
# date: 2013.12.23
# input:
#       source_path: source path
#       tgt_ld: target load name, it can be a file or folder
#       target_path: target path
# ------------------------------------------------------------------------------
import os
import shutil
import logging

import suntest.core.command as Command

logger = logging.getLogger(__name__)


def copy_file(source_path, target_path, file_name=''):
    """
    Description:
        copy source file to target path
    Return: (bool)
    Parameters:
        source_path: (str) source path.
        target_path: (str) target path.
        file_name: (str) the copy file.
    """
    if not isinstance(source_path, basestring):
        raise TypeError("source_path must be a string.")

    if not isinstance(target_path, basestring):
        raise TypeError("target_path must be a string.")

    if not os.path.exists(source_path):
        logger.error("%s is not exists." % source_path)
        return False
    if not os.path.exists(target_path):
        logger.error("%s is not exists." % target_path)
        return False

    copy_file_args = ["cp", "-avpf", os.path.join(source_path, file_name), target_path]
    return Command.execute_command(copy_file_args, timeout=60)


def copy_dir(source_path, target_path):
    """
    Description:
        copy source path to target path
    Return: (bool)
    Parameters:
        source_path: (str) source path.
        target_path: (str) target path.
    """
    if not isinstance(source_path, basestring):
        raise TypeError("source_path must be a string.")

    if not isinstance(target_path, basestring):
        raise TypeError("target_path must be a string.")

    if not os.path.exists(source_path):
        logger.error("%s is not exists." % source_path)
        return False
    if not os.path.exists(target_path):
        logger.error("%s is not exists." % target_path)
        return False

    for source_file in os.listdir(source_path):
        copy_file(source_path, target_path, source_file)

    return True


def copy_tree_with_fext(source_path, target_path, splitext='', exclude_dirs=[]):
    """
    Description:
        deep copy the specify file with ext from source path to target path.
    Return: (bool)
    Parameters:
        source_path: (str) source path.
        target_path: (str) target path.
        splitext: (str) file ext.
        exclude_dirs: (list) exclude directorys.
    """
    if not isinstance(source_path, basestring):
        raise TypeError("source_path must be a string.")

    if not isinstance(target_path, basestring):
        raise TypeError("target_path must be a string.")

    if not os.path.exists(source_path):
        logger.error("%s is not exists." % source_path)
        return False
    if not os.path.exists(target_path):
        logger.error("%s is not exists." % target_path)
        return False

    for name in os.listdir(source_path):
        srcname = os.path.join(source_path, name)
        dstname = os.path.join(target_path, name)
        try:
            if os.path.isdir(srcname):
                if os.path.basename(srcname) in exclude_dirs:
                    continue
                else:
                    copy_tree_with_fext(srcname, dstname, splitext, exclude_dirs)
            elif os.path.islink(srcname):
                continue
            elif os.path.isfile(srcname):
                fname, fextension = os.path.splitext(srcname)
                if fextension == splitext:
                    if not os.path.exists(os.path.dirname(dstname)):
                        os.makedirs(os.path.dirname(dstname))
                    shutil.copy2(srcname, dstname)
                    try:
                        shutil.copystat(source_path, target_path)
                    except Exception:
                        logger.exception("copystat error.")
                        continue
        except IOError:
            logger.exception("copy tree with file extention error.")
            continue

    return True


def copy_tree_with_fname(source_path, target_path, splitname=''):
    """
    Description:
        deep copy the specify file with ext from source path to target path.
    Return: (bool)
    Parameters:
        source_path: (str) source path.
        target_path: (str) target path.
        splitext: (str) file ext.
    """
    if not isinstance(source_path, basestring):
        raise TypeError("source_path must be a string.")

    if not isinstance(target_path, basestring):
        raise TypeError("target_path must be a string.")

    if not os.path.exists(source_path):
        logger.error("%s is not exists." % source_path)
        return False
    if not os.path.exists(target_path):
        logger.error("%s is not exists." % target_path)
        return False

    names = os.listdir(source_path)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    for name in names:
        srcname = os.path.join(source_path, name)
        dstname = os.path.join(target_path, name)
        try:
            if os.path.isdir(srcname):
                copy_tree_with_fname(srcname, dstname, splitname)
            elif os.path.islink(srcname):
                continue
            elif os.path.isfile(srcname):
                fname, fextension = os.path.splitext(srcname)
                if fname == splitname:
                    shutil.copy2(srcname, dstname)
        except IOError:
            logger.exception("copy tree with filename error.")
            continue
    try:
        shutil.copystat(source_path, target_path)
    except Exception:
        logger.exception("copystat error.")
        return False

    return True
