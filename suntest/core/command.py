# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: command.py
# Author:   huangbin@pset.suntec.net
# Date:     2015.5.22
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import time
import subprocess
import logging

logger = logging.getLogger(__name__)


def execute_command(command, timeout=1800):
    """
    Description:
        execute command
    Returns (status) of command.
    Parameters:
        command: (str)
            A concatenated string of executable and arguments.
        timeout: (int)
            timeout of execute command
    """
    if not isinstance(command, list):
        raise TypeError("command must be a list.")

    if not isinstance(timeout, int):
        raise TypeError("timeout must be an int.")

    timesec = timeout

    logger.debug(' '.join(command))
    try:
        p_command = subprocess.Popen(command, env=os.environ.copy())
        while True:
            if p_command.poll() is None:
                time.sleep(1)
                timesec = timesec - 1
                if timesec == 0:
                    logger.error("执行命令%s超时%d秒。" % (' '.join(command), timeout))
                    p_command.kill()
                    return False
            else:
                if p_command.returncode == 0:
                    logger.debug("执行命令%s成功。" % (' '.join(command)))
                    return True
                else:
                    logger.error("执行命令%s失败。" % (' '.join(command)))
                    return False
    except OSError as e:
        logger.exception("执行命令发生异常: %s." % e)
        raise


def shell_command(shell_command, stdout=None, stderr=None, timeout=1800):
    """
    Description:
        execute shell command
    Return (status) of shell command.
    Parameters
        shell_command: str
            A concatenated string of executable and arguments.
        stdout: str
            shell command popen stdout
        stderr: str
            shell command popen stderr
        timeout: int
            timeout of shell command
    """
    if not isinstance(shell_command, basestring):
        raise TypeError("shell_command must be a string.")

    if not isinstance(timeout, int):
        raise TypeError("timeout must be an int.")

    timesec = timeout

    logger.debug(shell_command)
    try:
        p_shell_command = subprocess.Popen(shell_command, shell=True, stdout=stdout, stderr=stderr, env=os.environ.copy())
        while True:
            if p_shell_command.poll() is None:
                time.sleep(1)
                timesec = timesec - 1
                if timesec == 0:
                    logger.error("执行shell命令%s超时%d秒。" % (shell_command, timeout))
                    p_shell_command.kill()
                    return False
            else:
                if p_shell_command.returncode == 0:
                    logger.debug("执行shell命令%s成功。" % (shell_command))
                    return True
                else:
                    logger.error("执行shell命令%s失败。" % (shell_command))
                    return False
    except Exception as e:
        logger.exception("执行shell命令发生异常: %s." % e)
        raise
