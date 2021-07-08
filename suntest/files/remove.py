# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: remove.py
# Author: huangbin@pset.suntec.net
# Date: 2014.2.8
# Input:
#       src_p: source path
#       tgt_ld: target load name, it can be a file or folder
#       tgt_p: target path
# ------------------------------------------------------------------------------
import os
import re
import logging

logger = logging.getLogger(__name__)

# argv[0]: match_file_name
# argv[1]: match_file_list


def find_files(argv, directory, file_list):
    """
    Description:
        file the specify files in the directory
    Return: (bool)
    Parameters:
        directory: (str) the target directory.
    """
    if not isinstance(directory, basestring):
        raise TypeError("directory must be a string.")

    if not os.path.isdir(directory):
        logger.warning("%s is not directory." % directory)
        return False

    try:
        for filename in file_list:
            filepath = os.path.join(directory, filename)
            if os.path.isdir(filepath):
                os.path.walk(filepath, find_files, argv)
            elif os.path.isfile(filepath):
                if filename.find(argv[0]) is not -1:
                    argv[1].append(filename)
            else:
                logger.warning("%s is neither file nor directory." % file)
    except Exception:
        logger.exception("find file error.")
        return False


def remove_files(argv, directory, filelist=[]):
    """
    Description:
        remove all files in the directory
    Return: (bool)
    Parameters:
        directory: (str) the target directory.
    """
    if not isinstance(directory, basestring):
        raise TypeError("directory must be a string.")

    if not os.path.isdir(directory):
        logger.warning("%s is not directory." % directory)
        return False

    try:
        for filename in filelist:
            filepath = os.path.join(directory, filename)
            if os.path.isdir(filepath):
                os.path.walk(filepath, remove_files, argv)
                os.rmdir(os.path.abspath(filepath))
            elif os.path.isfile(filepath):
                os.remove(filepath)
            else:
                continue
    except Exception:
        logger.exception("remove files error.")
        return False
    finally:
        return True


def remove_files_excl_dir(argv, directory, filelist=[]):
    """
    Description:
        remove all files exclude directory
    Return: (bool)
    Parameters:
        directory: (str) the target directory.
    """
    if not isinstance(directory, basestring):
        raise TypeError("directory must be a string.")

    if not os.path.isdir(directory):
        logger.warning("%s is not directory." % directory)
        return False

    if os.path.basename(directory) not in argv:
        for filename in filelist:
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                os.remove(os.path.abspath(filepath))


def remove_files_excl_file(argv, directory, filelist=[]):
    """
    Description:
        remove all files exclude directory
    Return: (bool)
    Parameters:
        directory: (str) the target directory.
    """
    if not isinstance(directory, basestring):
        raise TypeError("directory must be a string.")

    if not os.path.isdir(directory):
        logger.warning("%s is not directory." % directory)
        return False

    try:
        for filename in filelist:
            if os.path.isdir(os.path.join(directory, filename)):
                os.path.walk(os.path.join(directory, filename), remove_files_excl_file, argv)
                os.rmdir(os.path.abspath(os.path.join(directory, filename)))
            else:
                if os.path.isfile(os.path.join(directory, filename)):
                    if os.path.basename(os.path.join(directory, filename)) not in argv:
                        os.remove(os.path.join(directory, filename))
    except OSError as e:
        print e


def remove_files_excl_regex(argv, directory, filelist=[]):
    """
    Description:
        remove all files exclude directory
    Return: (bool)
    Parameters:
        directory: (str) the target directory.
    """
    if not isinstance(directory, basestring):
        raise TypeError("directory must be a string.")

    if not os.path.isdir(directory):
        logger.warning("%s is not directory." % directory)
        return False

    for filename in filelist:
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            if os.path.basename(filepath).find(argv) is not -1:
                continue
            else:
                os.remove(os.path.abspath(filepath))


def remove_all_files(directory):
    """
    Description:
        remove all files in the directory
    Return: (bool)
    Parameters:
        directory: (str) the target directory.
    """
    if not isinstance(directory, basestring):
        raise TypeError("directory must be a string.")

    if not os.path.isdir(directory):
        logger.warning("%s is not a directory." % directory)
        return False

    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            # if filepath is directory
            if os.path.isdir(filepath):
                remove_all_files(filepath)
                if not os.listdir(filepath):
                    os.rmdir(os.path.abspath(filepath))
            # if filepath is linkfile
            if os.path.islink(filepath):
                os.system('rm -rf %s' % filepath)
            # if filepath is regular file
            if os.path.isfile(filepath):
                os.remove(filepath)
    except Exception:
        logger.exception("remove all files error.")
        return False
    finally:
        return True


def remove_spc_files(directory, spcfile, exclude_dir=''):
    """
    Description:
        remove the specify files in the directory
    Return: (bool)
    Parameters:
        directory: (str) the target directory.
        spcfile: (str) the target filename.
        exclude_dir: (str) exclude directory.
    """
    if not isinstance(directory, basestring):
        raise TypeError("directory must be a string.")
    if not isinstance(spcfile, basestring):
        raise TypeError("spcfile must be a string.")

    if not os.path.isdir(directory):
        logger.warning("%s is not directory." % directory)
        return False

    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if filepath in exclude_dir:
                continue

            if os.path.isdir(filepath):
                remove_spc_files(filepath, spcfile, exclude_dir)
            else:
                m_spcfile = re.search(r'%s' % spcfile, filename)
                if m_spcfile:
                    if os.path.isfile(filepath):
                        logger.debug("删除文件: %s." % filepath)
                        os.remove(filepath)
    except Exception:
        logger.exception("remove specify files error.")
        return False
    finally:
        return True
