# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: testrunner.py
# Author:   huangbin@pset.suntec.net
# Date:     2020.6.12
# ------------------------------------------------------------------------------
import os
import logging

from suntest import ExitStatus
from suntest.core import exceptions
from suntest.config import settings

logger = logging.getLogger(__name__)


class TestRunner(object):
    def __init__(self, test_config, device):
        self.test_result_flag = ExitStatus.OK
        self._type = str(test_config.get("type", ""))

    @property
    def type(self):
        return self._type

    @property
    def device(self):
        return self._device

    def run(self, workspace):
        """
        Description:
            run the smoketest progress.
        Parameters:
            workspace: (str) test result store path.
        Return: (tool)
        """
        pass

