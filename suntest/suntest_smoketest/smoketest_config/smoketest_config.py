# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Module:   smoketest_config
# Author:   huangbin@pset.suntec.net
# Date:     2020.6.14
# Input:
#           None
# ------------------------------------------------------------------------------
import os
import logging
from yaml import safe_load
from yaml.scanner import ScannerError

logger = logging.getLogger(__name__)


class ConfigSmokeTest(object):
    def __init__(self, smoketest_config_file):
        try:
            with open(smoketest_config_file) as f:
                self.smoketest_config = safe_load(f)
        except IOError:
            logger.exception("%s不存在。" % smoketest_config_file)
            raise

    def get_tests_config(self):
        return self.smoketest_config.get("smoketest", [])

