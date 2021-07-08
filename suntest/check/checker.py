# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: checker.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.3.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import sys
import logging
from distutils.spawn import find_executable

from suntest.core import exceptions
from suntest.config import settings


class Checker(object):
    def __init__(self):
        pass

    def check_env(self):
        """
        Description:
            check unittest env.
        Return: (bool)
        """
        if not settings.compile_arch:
            return
        if not os.environ.get('%s_TOOLCHAIN' % settings.compile_arch):
            raise exceptions.NoLunchCombo("您还没有执行lunch命令。")

    def check_lcov(self):
        """
        Description:
            check lcov tool if or not installed.
        Return: (bool)
        """
        if not find_executable("lcov"):
            raise exceptions.NoInstallLcov("您还没有安装lcov工具。")

    def check_gcovr(self):
        """
        Description:
            check gcovr tool if or not installed.
        Return: (bool)
        """
        if not find_executable("gcovr"):
            raise exceptions.NoInstallGcovr("您还没有安装gcovr工具。")
