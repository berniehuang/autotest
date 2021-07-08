# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: project_unittest.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
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
from suntest.task.task import Task
from suntest.task.taskstate import TasksState
from suntest.build.compile_unittest import Compile_UnitTest
from suntest.build.compile_emulator import Compile_Emulator

from suntest.suntest_unittest.runner import TestRunnerFactory
from suntest.suntest_unittest.runner.junitrunner import JUnitRunner
from suntest.suntest_unittest.unittest_config.unittest_config import ConfigUnitTest
from suntest.suntest_unittest.unittest_result.unittest_result import UnitTestResult
from suntest.suntest_unittest.report.testreport_generator import TestReportGenerator
import suntest.suntest_unittest.report.uncovr as Uncovr

logger = logging.getLogger(__name__)


class ProjectUnitTest(Project):
    """
        a project manage unittest how to run.
        Parameters:
            name: (str) project name.
            workspace: (str) project workspace.
            device: (Device) the device for run unittest.
            unittest_config: (str) unittest config file.
    """
    all_tasks = ["emulator", "compile", "run", "report", "clean", "uncovr", "clear"]
    build_tasks = ["compile", "run", "report", "clean"]
    task_action = {'compile': Task(name="compile", dependon="emulator", actions=['compile_unittests']),
                   'run':     Task(name="run", dependon="compile", actions=['run_unittests']),
                   'report':  Task(name="report", dependon="run", actions=['generate_test_report']),
                   'clean':   Task(name="clean", actions=['clean_unittests']),
                   'clear':   Task(name="clear", actions=['clear_unittests']),
                   'emulator': Task(name="emulator", actions=['compile_emulator']),
                   'uncovr': Task(name="uncovr", actions=['generate_uncovr_report'])}

    def __init__(self, name, workspace, device, unittest_config, tasks):
        super(ProjectUnitTest, self).__init__(name, workspace)
        self.unittest_config = ConfigUnitTest(unittest_config)
        self.project_name = settings.project_name
        self.repository = self.unittest_config.get_repository()
        try:
            self.branch = Repo(self.repository).active_branch
        except TypeError as e:
            logger.warning("获取本地分支名失败")
            self.branch = os.environ.get("BRANCH", "")
        self.lunch_combo = '%s-%s' % (os.environ.get('TARGET_PRODUCT'), os.environ.get('TARGET_BUILD_VARIANT'))
        self.device = device
        tests = [TestRunnerFactory.get_test_object(test_config, device) for test_config in self.unittest_config.get_tests_config()]
        self.tests = [test for test in tests if re.search(ur"%s" % test.product_type, settings.product_type) \
                                                and (test.type == settings['test_type'] or not settings['test_type']) \
                                                and (test.project_name == settings.project_name or not test.project_name)]
        self.testreport = TestReportGenerator()
        self.testresult = UnitTestResult()
        if "build" in tasks:
            tasks = ProjectUnitTest.build_tasks
        if "all" in tasks:
            tasks = ProjectUnitTest.all_tasks
        self.tasks = [ProjectUnitTest.task_action.get(task) for task in tasks]
        self.build_tasks = [ProjectUnitTest.task_action.get(task) for task in ProjectUnitTest.build_tasks]
        TasksState.initial_tasks_state((set(tasks) >= set(ProjectUnitTest.build_tasks)), ProjectUnitTest.all_tasks)

    def about(self):
        print '=' * 110
        print '                                             --单体测试配置--'
        for test in self.tests:
            print test
            print ""
        print '=' * 110

    def skip_task(self, task):
        """
        Description:
            skip task in project.
        Return:
        """
        TasksState.notify_task_fail(task.name)

    def run_task(self, task):
        """
        Description:
            run task in project.
        Return:
        """
        if task.dependon:
            dependon_task = ProjectUnitTest.task_action.get(task.dependon)
            if TasksState.NG == dependon_task.get_state():
                self.run_task(dependon_task)
            if TasksState.FA == dependon_task.get_state():
                self.skip_task(task)
                return

        for action in task.get_actions():
            action_return = eval("self.%s" % action)()
            logger.debug("任务%s返回结果为%d" % (task.name, action_return))
            if action_return == ExitStatus.OK:
                TasksState.notify_task_done(task.name)
            else:
                self.result = action_return
                TasksState.notify_task_fail(task.name)

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
    def compile_unittests(self):
        """
        Description:
            compile all unittest programs in project.
        Return: (bool)
        """
        compile_unittest_object = Compile_UnitTest(settings['jobs'], os.path.join(self.workspace, "compile_unittest.log"), self.unittest_config)
        if compile_unittest_object.compile_unittest_with_coverage():
            return ExitStatus.OK
        else:
            return ExitStatus.COMPILE_ERROR

    @funcExecTime
    def clean_unittests(self):
        """
        Description:
            clean all unittests programs in project.
        Return: (bool)
        """
        compile_unittest_object = Compile_UnitTest(settings['jobs'], os.path.join(self.workspace, "compile_unittest.log"), self.unittest_config)
        if compile_unittest_object.clean_unittest():
            return ExitStatus.OK
        else:
            return ExitStatus.COMPILE_ERROR


    @funcExecTime
    def clear_unittests(self):
        """
        Description:
            clear all unittests results for the project.
        Return: (bool)
        """
        logger.info("开始清理单体测试生成文件。")
        if os.path.exists(settings['workspace']):
            os.path.walk(settings['workspace'], Remove.remove_files_excl_file, ("autotest.log"))

        for filename in [f for f in os.listdir(os.getcwd()) if os.path.isfile(f)]:
            filepath = os.path.join(os.getcwd(), filename)
            if re.search(r'device-.*.log', filename) or filename == "build.log":
                logger.debug('删除文件: %s.' % filepath)
                os.remove(filepath)

        repository_path = self.unittest_config.get_repository()
        if os.path.exists(repository_path):
            Remove.remove_spc_files(repository_path, ".*.gcno")
            Remove.remove_spc_files(repository_path, ".*.gcda")

        return ExitStatus.OK

    @funcExecTime
    def run_unittests(self):
        """
        Description:
            run all unittests for the project.
        Return: (ExitStatus) test result flag.
        """
        _test_results = list()

        for test in self.tests:
            self.testresult.flag = test.run(self.workspace)
            _test_results.append(self.testresult.flag)
            if self.testresult.flag == ExitStatus.DEVICE_STARTUP_FAILED:
                break

        try:
            return reduce(lambda x, y: x or y, _test_results)
        except TypeError as e:
            return ExitStatus.NO_MEET_TEST

    def combine_gtest_result_reports(self):
        """
        Description:
            combine all googletest unittest result reports into one report.
        """
        gtest_result_report = os.path.join(self.workspace, "gtest-result-%s.xml" % self.name)
        gtest_result_reports = list()
        for result_report in [os.path.join(self.workspace, test.result_report) for test in self.tests if test.type == "gtest"]:
            if not os.path.exists(result_report):
                raise exceptions.TestReportError("结果报告%s不存在" % result_report)
            gtest_result_reports.append(result_report)

        (cases, failures) = self.testreport.generate_gtest_result_report(gtest_result_report, gtest_result_reports)

        self.testresult.result.set((cases, failures))

    def combine_junit_result_reports(self):
        """
        Description:
            combine all junit unittest result reports into one report.
        """
        junit_result_report = os.path.join(self.workspace, "junit-result-%s.xml" % self.name)
        junit_result_reports = list()
        for result_report in [os.path.join(self.workspace, test.result_report) for test in self.tests if test.type == "junit"]:
            if not os.path.exists(result_report):
                raise exceptions.TestReportError("结果报告%s不存在" % result_report)
            junit_result_reports.append(result_report)
        (cases, failures) = self.testreport.generate_junit_result_report(junit_result_report, junit_result_reports)
        self.testresult.result.set((cases, failures))

    def combine_qtest_result_reports(self):
        """
        Description:
            combine all qt unittest result reports into one report.
        """
        qtest_result_report = os.path.join(self.workspace, "qtest-result-%s.xml" % self.name)
        qtest_result_reports = list()
        for result_report in [os.path.join(self.workspace, test.result_report) for test in self.tests if test.type == "qtest" or test.type == "qtapptest"]:
            if not os.path.exists(result_report):
                raise exceptions.TestReportError("结果报告%s不存在" % result_report)
            qtest_result_reports.append(result_report)

        (cases, failures) = self.testreport.generate_qtest_result_report(qtest_result_report, qtest_result_reports)

        self.testresult.result.set((cases, failures))

    def combine_cobertura_coverage_reports(self):
        """
        Description:
            combine all cobertura coverage reports into one report.
        """
        cobertura_coverage_report = os.path.join(self.workspace, "test-coverage-%s.xml" % self.name)
        gcov_cobertura_coverage_report = os.path.join(self.workspace, "test-gcov-%s.xml" % self.name)
        jacoco_cobertura_coverage_report = os.path.join(self.workspace, "test-jacoco-%s.xml" % self.name)

        cobertura_coverage_reports = list()
        cpp_tests = [test for test in self.tests if test.type == "gtest" or test.type == "qtest"]
        if cpp_tests:
            if not os.path.exists(gcov_cobertura_coverage_report):
                raise exceptions.CoverageReportError("c/c++覆盖率报告%s不存在" % gcov_cobertura_coverage_report)
            else:
                cobertura_coverage_reports.append(gcov_cobertura_coverage_report)
        junit_tests = [test for test in self.tests if test.type == "junit"]
        if junit_tests:
            if not os.path.exists(jacoco_cobertura_coverage_report):
                raise exceptions.CoverageReportError("java覆盖率报告%s不存在" % jacoco_cobertura_coverage_report)
            else:
                cobertura_coverage_reports.append(jacoco_cobertura_coverage_report)

        self.testreport.generate_cobertura_coverage_report(cobertura_coverage_report, cobertura_coverage_reports)

    def generate_repository_coverage_report_with_lcov(self):
        """
        Description:
            generate repository code coverage report with lcov.
        """
        repository = self.unittest_config.repository
        cobertura_report_filename = os.path.join(self.workspace, "test-lcov-%s" % self.name)
        lcov_exclude_list = list(chain(*[test.lcov_exclude for test in self.tests]))
        lcov_filter_list = list(chain(*[test.lcov_filter for test in self.tests]))
        trace_file = os.path.join(self.workspace, "test-lcov-%s.info" % self.name)
        lcov_result = os.path.join(self.workspace, "test-lcov-%s_result" % self.name)

        (line_rate, line_cover, line_total, branch_rate, branch_cover, branch_total) = \
        self.testreport.generate_code_coverage_report_with_lcov(repository, cobertura_report_filename, lcov_exclude_list, lcov_filter_list, trace_file, lcov_result)

    def generate_repository_coverage_report_with_gcovr(self):
        """
        Description:
            generate repository code coverage report with gcovr.
        """
        repository = self.unittest_config.repository
        code_coverage_report_filename = os.path.join(self.workspace, "test-gcov-%s" % self.name)
        gcov_exclude_list = list(chain(*[test.gcov_exclude for test in self.tests]))
        gcov_filter_list = list(chain(*[test.gcov_filter for test in self.tests]))

        (line_rate, line_cover, line_total, branch_rate, branch_cover, branch_total) = \
        self.testreport.generate_code_coverage_report_with_gcovr(repository, code_coverage_report_filename, gcov_exclude_list, gcov_filter_list)

        self.testresult.coverage.set(((line_rate, line_cover, line_total, branch_rate, branch_cover, branch_total)))

    def generate_repository_coverage_report_with_jacoco(self):
        """
        Description:
            generate repository code coverage report with jacoco.
        """
        code_coverage_report = os.path.join(self.workspace, "test-jacoco-%s.xml" % self.name)
        javanote_files = filter(os.path.exists, [os.path.join(self.workspace, test.get_javanote_filename()) for test in self.tests if test.type == "junit"])
        execution_files = filter(os.path.exists, [os.path.join(self.workspace, test.coverage_ec) for test in self.tests if test.type == "junit"])
        source_dirs = [path for test in self.tests if test.type == "junit" \
                       for path in (test.source_code_path.split() if isinstance(test.source_code_path, str) else test.source_code_path)]
        report_dir = self.workspace
        source_root = self.unittest_config.repository

        if len(execution_files) == 0:
            logger.warning("coverage.ec文件不存在。")
            return
        if len(javanote_files) == 0:
            logger.warning("javanote文件不存在。")
            return

        (line_rate, line_cover, line_total, branch_rate, branch_cover, branch_total) = \
        self.testreport.generate_code_coverage_report_with_jacoco(code_coverage_report, javanote_files, execution_files, source_dirs, report_dir, source_root)

        self.testresult.coverage.set(((line_rate, line_cover, line_total, branch_rate, branch_cover, branch_total)))

    @funcExecTime
    def generate_test_report(self):
        """
        Description:
            generate overall unittest result report and code coverage report.
        """
        try:
            self.combine_gtest_result_reports()
            self.combine_qtest_result_reports()
            self.combine_junit_result_reports()

            if settings['lcov']:
                self.generate_repository_coverage_report_with_lcov()
            if settings['gcov']:
                self.generate_repository_coverage_report_with_gcovr()
            if settings['jacoco']:
                self.generate_repository_coverage_report_with_jacoco()

            self.combine_cobertura_coverage_reports()

            if self.result == ExitStatus.OK:
                if self.testresult.result.cases != 0 and self.testresult.result.failures == 0:
                    self.result = ExitStatus.OK
                else:
                    self.result = ExitStatus.CASE_FAILURE
        except exceptions.TestReportError:
            return ExitStatus.TEST_REPORT_NOT_FOUND
        except exceptions.CoverageReportError:
            return ExitStatus.COVERAGE_REPORT_NOT_FOUND
        except Exception as e:
            print e
            return ExitStatus.OTHER_ERROR
        return self.result

    @funcExecTime
    def generate_uncovr_report(self):
        """
        Description:
            generate uncovered code report
        Return: (bool)
        """
        Uncovr.capture_uncovered_code(os.path.join(self.workspace, "test-coverage-%s.xml" % self.name), \
                                      os.path.join(self.workspace, "uncovered-%s.xlsx" % self.name))
        return ExitStatus.OK

    def get_unittest_result_dataframe(self):
        """
        Description:
            get unittest result dataframe
        Return: (DataFrame) test result dataframe.
        """
        _unittest_result_head = ["project", "branch", "repository", "combo", "result", "test_cases", "test_failures",
                                 "line_rate", "line_cover", "line_total", "branch_rate", "branch_cover", "branch_total"]

        _result = ExitStatus.EXIT_STATUS_CHN.get(self.result)
        try:
            _line_rate = float(self.testresult.line_cover) / float(self.testresult.line_total)
            _line_rate = round(_line_rate, 2)
            _branch_rate = float(self.testresult.branch_cover) / float(self.testresult.branch_total)
            _branch_rate = round(_branch_rate, 2)
        except ZeroDivisionError as e:
            _line_rate = _branch_rate = round(float(0), 2)

        _unittest_result_list = [[self.project_name, self.branch, self.repository, self.lunch_combo,
                                 _result, self.testresult.test_cases, self.testresult.test_failures,
                                 _line_rate, self.testresult.line_cover, self.testresult.line_total,
                                 _branch_rate, self.testresult.branch_cover, self.testresult.branch_total]]

        df = pd.DataFrame.from_records(_unittest_result_list, columns=_unittest_result_head)
        return df

    def get_unittest_duration_dataframe(self):
        def read_unittest_duration_csv(csv_file):
            with open(csv_file,'r') as f:
                reader = csv.reader(f)
                fieldnames = next(reader)
                csv_reader = csv.DictReader(f, fieldnames=fieldnames)
                task_name_list = list()
                duration_list = list()
                for row in csv_reader:
                    task_name_list.extend([v for k,v in row.items() if k == "task_name"])
                    duration_list.extend([v for k,v in row.items() if k == "duration"])

            return (task_name_list, duration_list)

        (_unittest_duration_head, _unittest_duration_list) = read_unittest_duration_csv("duration.csv")
        _unittest_duration_head.append("project")
        _unittest_duration_list.append(self.project_name)
        _unittest_duration_list = [_unittest_duration_list]
        df = pd.DataFrame.from_records(_unittest_duration_list, columns=_unittest_duration_head)
        return df
        
    def get_test_result(self):
        """
        Description:
            get unittest result for the project.
        Return: (ExitStatus) test result flag.
        """
        df_duration = self.get_unittest_duration_dataframe()
        df_unittest = self.get_unittest_result_dataframe()

        df = pd.merge(df_unittest, df_duration)

        df.to_csv(os.path.join(self.workspace, 'unittest.csv'), index=False)
        Write.write_file(os.path.join(self.workspace, 'unittest.flag'), ExitStatus.EXIT_STATUS_CHN.get(self.result))

    def print_summary(self):
        """
        Description:
            get test result summary
        """
        print '=' * 110
        print '                                             --测试结果概要--'
        print '                                           %s' % Time.get_current_time()
        print '[项目]: %s' % self.project_name
        print '[分支]: %s' % self.branch
        print '[仓库]: %s' % self.repository
        print '[产品类型]: %s' % self.lunch_combo
        print '[测试结果]: %s' % ExitStatus.EXIT_STATUS_CHN.get(self.result)
        print self.testresult
        print '=' * 110

    def __del__(self):
        if os.path.exists("duration.csv"):
            os.remove("duration.csv")
        return
