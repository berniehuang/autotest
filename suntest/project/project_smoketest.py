# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: project_smoketest.py
# Author:   huangbin@pset.suntec.net
# Date:     2020.6.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import re
import csv
import logging

from distutils.spawn import find_executable
from itertools import chain
from git import Repo
import pandas as pd
import numpy as np

from suntest import ExitStatus
from suntest.core import exceptions
from suntest.config import settings
import suntest.util.functime as Time
import suntest.files.remove as Remove
import suntest.files.write as Write
from suntest.util.functime import funcExecTime
from suntest.project.project import Project
from suntest.build.compile_emulator import Compile_Emulator
from suntest.task.task import Task
from suntest.suntest_smoketest.runner import TestRunnerFactory
from suntest.suntest_smoketest.runner.emurunner import EmuRunner
from suntest.suntest_smoketest.smoketest_config.smoketest_config import ConfigSmokeTest

logger = logging.getLogger(__name__)


class ProjectSmokeTest(Project):
    """
        a project manage smoketest how to run.
        Parameters:
            name: (str) project name.
            workspace: (str) project workspace.
            device: (Device) the device for run unittest.
            unittest_config: (str) unittest config file.
    """
    task_action = {'compile': Task(name="compile", actions=['compile_emulator']),
                   'test': Task(name="test", actions=['test_emulator'])}

    def __init__(self, name, workspace, device, config, tasks):
        super(ProjectSmokeTest, self).__init__(name, workspace)
        self.project_name = settings.project_name
        self.device = device
        self.tasks = [ProjectSmokeTest.task_action.get(task) for task in tasks]
        self.smoketest_config = ConfigSmokeTest(config)
        self.tests = [TestRunnerFactory.get_test_object(test_config, device) for test_config in self.smoketest_config.get_tests_config()]

    def about(self):
        print '=' * 110
        print '                                             --冒烟测试配置--'
        for test in self.tests:
            print test
            print ""
        print '=' * 110

    def run_task(self, task):
        """
        Description:
            run task in project.
        Return:
        """
        for action in task.get_actions():
            action_return = eval("self.%s" % action)()
            logger.debug("任务%s返回结果为%d" % (task.name, action_return))
            self.result = action_return

    @funcExecTime
    def compile_emulator(self):
        """
        Description:
            compile emulator for run unittests.
        Return: (bool)
        """
        compile_emulator_object = Compile_Emulator(settings['jobs'], os.path.join(self.workspace, "compile_emulator.log"))
        if compile_emulator_object.compile_emulator():
            return ExitStatus.OK
        else:
            return ExitStatus.COMPILE_EMU_ERROR

    @funcExecTime
    def test_emulator(self):
        """
        Description:
            run all unittests for the project.
        Return: (ExitStatus) test result flag.
        """
        for test in self.tests:
            result = test.run()
            if result != ExitStatus.OK:
                return result

        return result

    def get_test_result(self):
        """
        Description:
            get unittest result for the project.
        Return: (ExitStatus) test result flag.
        """
        pass

    def print_summary(self):
        """
        Description:
            get test result summary
        """
        print '=' * 110
        print '                                             --测试结果概要--'
        print '                                           %s' % Time.get_current_time()
        print '[项目]: %s' % self.project_name
        print '[测试结果]: %s' % ExitStatus.EXIT_STATUS_CHN.get(self.result)
        print '=' * 110


    def __del__(self):
        return
