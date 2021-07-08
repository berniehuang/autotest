# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: testreport_generator.py
# Author:   huangbin@iauto.com
# Date:     2019.2.27
# ------------------------------------------------------------------------------
import os
import re
import logging
import webbrowser
from ConfigParser import ConfigParser
from suntest.core import exceptions
from suntest.config import settings
from suntest.tools import TOOLS_PATH
from suntest.suntest_unittest.report.result_report import ResultReport
from suntest.suntest_unittest.report.coverage_report import CoverageReport
from suntest.suntest_unittest.report.gcovr_report import GcovrReport
from suntest.suntest_unittest.report.lcov_report import LcovReport
from suntest.suntest_unittest.report.jacoco_report import JacocoReportFactory

logger = logging.getLogger(__name__)


class TestReportGenerator(object):
    def __init__(self):
        if settings.gcov_executable:
            self.gcov_executable = settings.gcov_executable
        else:
            self.gcov_executable = os.path.join(os.environ.get('%s_TOOLCHAIN' % settings.compile_arch), "%s-gcov" % settings.toolchain)
        if not os.path.exists(self.gcov_executable):
            logger.error("%s是不存在的。" % self.gcov_executable)
            raise IOError

    def generate_gtest_result_report(self, gtest_result_report, gtest_result_reports):
        """
        Description:
            generate overall unittest result reports for the project.
        Parameters:
            gtest_result_report: (str) googletest result report filename.
            gtest_result_report: (list) googletest result report file list.
        Return: (tuple) test case number and failure case number
        """
        result_report = ResultReport()
        result_report.set_gtest_result_report(gtest_result_report)

        # combine gtest_result_reports
        readxmlstrs = result_report.read_result_reports(gtest_result_reports)
        xmlstr = result_report.combine_gtest_result_reports(readxmlstrs)
        result_report.write_result_report(xmlstr, gtest_result_report)

        if os.path.exists(gtest_result_report):
            return result_report.parse_junit_result_report(result_report.gtest_result_report)

    def generate_junit_result_report(self, junit_result_report, junit_result_reports):
        """
        Description:
            generate overall junit unittest result reports for the project.
        Parameters:
            junit_result_report: (str) junit result report filename.
            junit_result_report: (list) junit result report file list.
        Return: (tuple) test case number and failure case number
        """
        result_report = ResultReport()
        result_report.set_junit_result_report(junit_result_report)

        # combine junit_result_reports
        readxmlstrs = result_report.read_result_reports(junit_result_reports)
        xmlstr = result_report.combine_junit_result_reports(readxmlstrs)
        result_report.write_result_report(xmlstr, junit_result_report)

        if os.path.exists(junit_result_report):
            return result_report.parse_junit_result_report(result_report.junit_result_report)

    def generate_qtest_result_report(self, qtest_result_report, qtest_result_reports):
        """
        Description:
            generate overall unittest result reports for the project.
        Parameters:
            qtest_result_report: (str) qt test result report filename.
            qtest_result_reports: (list) qt test result report file list.
        Return: (tuple) test case number and failure case number
        """
        result_report = ResultReport()
        result_report.set_qtest_result_report(qtest_result_report)

        # combine qtest_result_reports
        readxmlstrs = result_report.read_result_reports(qtest_result_reports)
        xmlstr = result_report.combine_qtest_result_reports(readxmlstrs)
        result_report.write_result_report(xmlstr, qtest_result_report)

        if os.path.exists(qtest_result_report):
            return result_report.parse_qt_result_report(result_report.qtest_result_report)

    def generate_cobertura_coverage_report(self, cobertura_coverage_report, cobertura_coverage_reports):
        """
        Description:
            generate overall cobertura coverage reports for the project.
        Parameters:
            cobertura_coverage_report: (str) cobertura coverage report filename for the project.
            coberture_coverage_reports: (list) cobertura coverage report file list.
        Return: (tuple) test case number and failure case number
        """
        coverage_report = CoverageReport()
        coverage_report.set_cobertura_coverage_report(cobertura_coverage_report)

        # combine cobertura_coverage_reports
        readxmlstrs = coverage_report.read_cobertura_coverage_reports(cobertura_coverage_reports)
        xmlstr = coverage_report.combine_cobertura_coverage_reports(readxmlstrs)
        coverage_report.write_cobertura_coverage_report(xmlstr, cobertura_coverage_report)

    def generate_code_coverage_report_with_lcov(self, repository, cobertura_report_filename, lcov_exclude_list, lcov_filter_list, trace_file, lcov_result):
        """
        Description:
            generate code coverage html format report with lcov tool.
        Parameters:
            repository: (str) repository local path.
            cobertura_report_filename: (str) cobertura coverage report filename with lcov.
            lcov_exclude_list: (list) exclude pattern list in code coverage report.
            trace_file: (str) googletest result report filename.
            lcov_result: (str) qt test result report filename.
        Return: (tool)
        """
        report_type = settings["report_type"]
        lcov_report = LcovReport(repository, self.gcov_executable, trace_file, lcov_result)
        coverage_report_file = "%s.%s" % (cobertura_report_filename, report_type)

        # feature for filter change files
        def read_gcov_filter_config(gcov_filter_config_file, section):
            if os.path.exists(gcov_filter_config_file):
                try:
                    config = ConfigParser()
                    config.read(gcov_filter_config_file)
                    lcov_filter_list.extend(gcov_filter_file for gcov_filter_file in config.get(section, "gcov_filter_files").split(","))
                except Exception as e:
                    logger.exception("get gcov filter files exception %s." % e)
                    raise

        if settings['gcov_filter']:
            read_gcov_filter_config(settings['gcov_filter'], settings['gcov_filter_section'])

        lcov_report.capture_gcda_files()
        lcov_report.extract_data_from_trace(lcov_filter_list)
        lcov_report.remove_data_from_trace(lcov_exclude_list)

        if report_type == "html":
            lcov_report.generate_lcov_html()
            coverage_report_file = os.path.join(lcov_result, "index.html")
            webbrowser.open(coverage_report_file)
        if report_type == "xml":
            lcov_report.generate_lcov_xml(coverage_report_file)

        return lcov_report.parse_cobertura_coverage_report(coverage_report_file, report_type)

    def generate_code_coverage_report_with_gcovr(self, repository, coverage_report_filename, gcov_exclude_list, gcov_filter_list):
        """
        Description:
            generate code coverage xml format report with gcovr tool.
        Parameters:
            repository: (str) repository path.
            coverage_report_filename: (str) code coverage report filename with gcovr.
            gcov_exclude_list: (list) exclude pattern list in code coverage report.
            gcov_filter_list: (list) filter pattern list in code coverage report.
        Return: (tuple) line rate, line cover, line total and branch rate, branch cover, branch total.
        """
        report_type = settings["report_type"]
        gcovr_report = GcovrReport(self.gcov_executable)
        coverage_report_file = "%s.%s" % (coverage_report_filename, report_type)

        # feature for filter change files
        def read_gcov_filter_config(gcov_filter_config_file, section):
            if os.path.exists(gcov_filter_config_file):
                try:
                    config = ConfigParser()
                    config.read(gcov_filter_config_file)
                    gcov_filter_list.extend(os.path.join(repository, gcov_filter_file) for gcov_filter_file in config.get(section, "gcov_filter_files").split(","))
                except Exception as e:
                    logger.exception("get gcov filter files exception %s." % e)
                    raise

        if settings['gcov_filter']:
            read_gcov_filter_config(settings['gcov_filter'], settings['gcov_filter_section'])

        gcovr_report.generate_coverage_report(coverage_report_file, repository, gcov_exclude_list, gcov_filter_list, report_type)

        if report_type == "html":
            webbrowser.open(coverage_report_file)

        return gcovr_report.parse_cobertura_coverage_report(coverage_report_file, report_type)

    def generate_code_coverage_report_with_jacoco(self, coverage_report_file, javanote_files, execution_files, source_dirs, report_dir, source_root):
        """
        Description:
            generate code coverage xml format report with jacoco tool.
        Parameters:
            coverage_report_file: (str) code coverage report filename with jacoco.
            javanote_files: (list) java note files.
            execution_files: (list) coverage ec filepath list.
            source_dirs: (list) source code directorys.
            report_dir: (str) coverage report location directory.
            source_root: (str) coverage report source root.
        """
        _report_type = settings['report_type']
        _jacoco_reporter = settings.jacoco_reporter or os.path.join(TOOLS_PATH, 'jacoco-cli.jar')
        _android_version = settings.android_version

        if not os.path.exists(_jacoco_reporter):
            logger.error("%s不存在。" % _jacoco_reporter)
            raise IOError

        jacoco_report = JacocoReportFactory.get_jacoco_report(_android_version, _jacoco_reporter, _report_type)

        jacoco_report.generate_coverage_report(javanote_files, execution_files, source_dirs, report_dir)
        if _report_type == "html":
            webbrowser.open(os.path.join(report_dir, "index.html"))
        if _report_type == "xml":
            jacoco_coverage_report = os.path.join(report_dir, "report.xml")
            if os.path.exists(jacoco_coverage_report):
                jacoco_report.transfer_jacoco_2_cobertura(source_root, source_dirs, jacoco_coverage_report, coverage_report_file)
            else:
                logger.error("%s不存在." % jacoco_coverage_report)
                return

        return jacoco_report.parse_cobertura_coverage_report(coverage_report_file, _report_type)
