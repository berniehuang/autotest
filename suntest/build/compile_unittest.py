# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: compile_unittest.py
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
from suntest.config import settings
from suntest.build.compile import Compile
from suntest.suntest_unittest.unittest_config.unittest_config import ConfigUnitTest

logger = logging.getLogger(__name__)


class Compile_UnitTest(Compile):
    def __init__(self, jobs, log_file, unittest_config):
        super(Compile_UnitTest, self).__init__(jobs, log_file)
        self.repository = unittest_config.get_repository()
        self.unittest_configs = unittest_config.get_tests_config()
        self.build_env = unittest_config.get_build_env() or settings['build_env']

    def get_build_targets(self):
        _build_targets = list()

        for unittest_config in self.unittest_configs:
            if unittest_config.has_key("test_library_files"):
                _build_targets.extend([library.get("compile_module_name", library.get("name").split('.')[0]) for library in unittest_config['test_library_files']])
            if unittest_config.has_key("test_case_file"):
                _build_targets.append(unittest_config['test_case_file'].get("name"))
            if unittest_config.has_key("test_package"):
                _build_targets.append(unittest_config['test_package'].get("name").split('.')[0])
            if unittest_config.has_key("code_packages"):
                _build_targets.extend([package.get("name").split('.')[0] for package in unittest_config['code_packages']])

        _build_targets = list(set(_build_targets))
        return _build_targets

    def compile_unittest_with_coverage(self):
        """
        Description:
            compile the unittest programs with coverage.
        Return: (tool)
        """
        _build_targets = self.get_build_targets()
        if len(_build_targets) == 0:
            logging.error("编译单体测试目标是空的。")
            return False

        logging.info("开始清编译单体测试程序...")
        return_code = self.make_clean(_build_targets)
        if not return_code:
            logging.error("清编译单体测试程序失败。")
            return False
        else:
            logging.info("清编译单体测试程序成功。")

        logging.info("开始编译单体测试程序...")

        if "framework/service/navi" not in self.repository:
            return_code = self.make_compile(_build_targets, self.build_env)
            if not return_code:
                logging.error("编译单体测试程序失败。")
            else:
                logging.info("编译单体测试程序成功。")
        else:
            logging.debug("build targets has navi module and need to compile separately.")
            for _build_target in _build_targets:
                return_code = self.make_compile(_build_target, self.build_env)
                if not return_code:
                    logging.error("编译单体测试程序失败。")
                    break
                else:
                    logging.info("编译单体测试程序成功。")

        return return_code

    def clean_unittest(self):
        """
        Description:
            clean the unittest programs.
        Return: (tool)
        """
        _build_targets = self.get_build_targets()
        if len(_build_targets) == 0:
            logging.error("编译目标是空的.")
            return False

        logging.info("开始清编译单体测试程序...")
        return_code = self.make_clean(_build_targets)
        if not return_code:
            logging.error("清编译单体测试程序失败。")
        else:
            logging.info("清编译单体测试程序成功。")

        return return_code
