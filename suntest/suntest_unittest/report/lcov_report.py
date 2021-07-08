# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: lcov_report.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import logging

import suntest.core.command as Command
from suntest.config import settings
from coverage_report import CoverageReport
from lcov2cobertura import Lcov2Cobertura

logger = logging.getLogger(__name__)


class LcovReport(CoverageReport):
    def __init__(self, repository, gcov_executable, trace_file, lcov_result):
        self.name = repository.replace("/", "_")
        self.repository = repository
        self.gcov_executable = gcov_executable
        self.trace_file = trace_file
        self.lcov_result = lcov_result

    def capture_gcda_files(self):
        logger.debug("开始抓取gcda文件生成lcov信息文件...")

        lcov_capture_gcda_args = ["lcov", "--gcov-tool=%s" % self.gcov_executable, "-c", "-d", self.repository, "--rc", "lcov_branch_coverage=1", "-t", self.name, "-o", self.trace_file]
        Command.execute_command(lcov_capture_gcda_args, timeout=300)

    def extract_data_from_trace(self, filters=[]):
        """
        Description:
            extract match pattern files in lcov result info.
        Return: (bool)
        Parameters:
            filters: (list) filter pattern list
        """
        _default_filters = ["*"]
        if len(filters) == 0:
            filters = _default_filters

        logger.debug("从trace_file文件中提取数据...")

        lcov_extract_data_args = ["lcov", "--gcov-tool=%s" % self.gcov_executable, "--extract", self.trace_file, "--rc", "lcov_branch_coverage=1", "-t", self.name, "-o", self.trace_file]

        pattern_list = ["%s/%s" % (os.path.abspath(self.repository), filter) for filter in filters]
        for pattern in pattern_list:
            lcov_extract_data_args.insert(4, pattern)

        Command.execute_command(lcov_extract_data_args, timeout=300)

    def remove_data_from_trace(self, excludes=[]):
        """
        Description:
            remove match pattern files in lcov result info.
        Return: (bool)
        Parameters:
            excludes: (list) exclude pattern list
        """
        logger.debug("从trace_file文件中剔除数据...")

        lcov_remove_data_args = ["lcov", "--gcov-tool=%s" % self.gcov_executable, "--remove", self.trace_file, "--rc", "lcov_branch_coverage=1", "-t", self.name, "-o", self.trace_file]

        pattern_list = ["%s/%s" % (os.path.abspath(self.repository), exclude) for exclude in excludes]
        for pattern in pattern_list:
            lcov_remove_data_args.insert(4, pattern)

        Command.execute_command(lcov_remove_data_args, timeout=300)

    def generate_lcov_html(self):
        logger.debug("生成lcov的html报告...")

        lcov_genhtml_args = ["genhtml", "-q", self.trace_file, "--legend", "--highlight", "--branch-coverage", "--no-function-coverage", "-o", self.lcov_result]
        Command.execute_command(lcov_genhtml_args, timeout=300)
        logger.info("lcov工具生成的覆盖率报告: %s/index.html" % self.lcov_result)

    def generate_lcov_xml(self, cobertura_report_filename):
        logger.debug("生成lcov的xml报告...")

        try:
            with open(self.trace_file, 'r') as lf:
                lcov_data = lf.read()
                lcov2cobertura = Lcov2Cobertura(lcov_data, self.repository)
                cobertura_xml_strings = lcov2cobertura.convert()
            with open(cobertura_report_filename, 'wt') as cf:
                cf.write(cobertura_xml_strings)
        except IOError as e:
            logger.exception("不能将lcov的html报告转成xml报告.")
            raise
