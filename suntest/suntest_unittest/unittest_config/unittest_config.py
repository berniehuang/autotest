# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Module:   unittest_config
# Author:   huangbin@pset.suntec.net
# Date:     2016.11.14
# Input:
#           None
# ------------------------------------------------------------------------------
import os
import logging
from yaml import safe_load
from yaml.scanner import ScannerError

logger = logging.getLogger(__name__)


class ConfigUnitTest(object):
    def __init__(self, unittest_config_file):
        try:
            with open(unittest_config_file) as f:
                self.unittest_config = safe_load(f)
                self.version = self.unittest_config.get("version", "1.0")
                self.repository = self.unittest_config.get("repository", "")
        except IOError:
            logger.exception("%s不存在。" % unittest_config_file)
            raise
        except ScannerError:
            logger.exception("单体测试配置文件%s中有选项没有对齐。" % unittest_config_file)
            raise

    def get_tests_config(self):
        return self.unittest_config.get("unittest", [])

    def get_repository(self):
        return self.unittest_config.get("repository", "")

    def get_build_env(self):
        build_env = str()

        try:
            build_env = self.unittest_config["build"]["build-env"]
        except KeyError as e:
            logger.warning("提醒: 选项%s没有在单体测试配置文件中设置。" % e)
        finally:
            return build_env
