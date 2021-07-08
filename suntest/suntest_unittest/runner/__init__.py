# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Module:   suntest_unittest
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
from suntest.suntest_unittest.runner.gtestrunner import GtestRunner
from suntest.suntest_unittest.runner.qtestrunner import QtestRunner
from suntest.suntest_unittest.runner.qtapptestrunner import QtApptestRunner
from suntest.suntest_unittest.runner.junitrunner import JUnitRunner


class TestRunnerFactory(object):
    operator = {'gtest': GtestRunner,
                'qtest': QtestRunner,
                'qtapptest': QtApptestRunner,
                'junit': JUnitRunner}

    @staticmethod
    def get_test_object(test_config, device):
        return TestRunnerFactory.operator.get(str(test_config.get("type", "")), 'gtest')(test_config, device)
