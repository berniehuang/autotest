# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: compile.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.3.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import sys
import time
import subprocess
import multiprocessing
import logging

import suntest.core.command as Command
import suntest.files.read as Read
from suntest.config import settings

logger = logging.getLogger(__name__)


class Compile(object):
    def __init__(self, jobs, log_file):
        if jobs:
            self.cpu_jobs = int(jobs)
        else:
            self.cpu_jobs = multiprocessing.cpu_count()
        self.build_log_file = log_file
        if os.path.exists(self.build_log_file):
            os.remove(self.build_log_file)
        self.build_log_fd = open(self.build_log_file, "a+")

    def make_compile(self, target, instrument=None):
        """
        Description:
            compile target with makefile base on android system.
        Return: (bool)
        Parameters:
            target: (str) the target of compile.
        """
        if isinstance(target, (list)):
            compile_target = ' '.join(target)
        elif isinstance(target, (str)):
            compile_target = target
        else:
            logger.error("编译目标类型是未知的。")
            return False

        if instrument is None:
            make_compile_cmd = "make %s -j%d" % (compile_target, self.cpu_jobs)
        else:
            make_compile_cmd = "%s make %s -j%d" % (instrument, compile_target, self.cpu_jobs)

        if Command.shell_command(make_compile_cmd, stdout=self.build_log_fd, stderr=self.build_log_fd, timeout=21600):
            return True
        else:
            Read.display_file(self.build_log_file, title="编译日志")
            return False

    def make_clean(self, target):
        """
        Description:
            clean target with makefile base on android system.
        Return: (bool)
        Parameters:
            target: (str) the target of clean.
        """
        if isinstance(target, (list)):
            clean_target = ' '.join(["clean-%s" % t for t in target])
        elif isinstance(target, (str)):
            clean_target = ' '.join(["clean-%s" % t for t in target.split(' ')])
        else:
            logger.error("清编译目标类型是未知的。")
            return False

        make_clean_cmd = "make %s -j%d" % (clean_target, self.cpu_jobs)
        if Command.shell_command(make_clean_cmd, stdout=self.build_log_fd, stderr=self.build_log_fd):
            return True
        else:
            Read.display_file(self.build_log_file, title="编译日志")
            return False

    def __del__(self):
        self.build_log_fd.close()
