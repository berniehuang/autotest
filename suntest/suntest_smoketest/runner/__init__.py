# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Module:   suntest_smoketest
# Author:   huangbin@pset.suntec.net
# Date:     2020.6.15
# Input:
#      None
# ------------------------------------------------------------------------------
from suntest.suntest_smoketest.runner.emurunner import EmuRunner


class TestRunnerFactory(object):
    operator = {'emulator': EmuRunner}

    @staticmethod
    def get_test_object(test_config, device):
        return TestRunnerFactory.operator.get(str(test_config.get("type", "")), 'emulator')(test_config, device)
