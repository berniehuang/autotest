# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: gcovr_report.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import shlex
import logging
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import suntest.core.command as Command
from suntest.config import settings
from coverage_report import CoverageReport

logger = logging.getLogger(__name__)


class GcovrReport(CoverageReport):
    def __init__(self, gcov_executable):
        self.gcov_executable = gcov_executable

    def generate_coverage_report(self, coverage_report_file, root_dir=os.getcwd(), excludes=[], filters=[], report_type="xml"):
        """
        Description:
            generate coverage report with gcovr tool.
        Return: (bool)
        Parameters:
            coverage_report_file: (str) coverage report filename.
            root_dir: (str) root directory
            excludes: (list) exclude pattern list
            filters: (list) filter pattern list
            report_type: coverage report type.
        """
        logger.info("gcovr工具生成的覆盖率报告: %s." % coverage_report_file)

        if report_type == "xml":
            gcovr_command = "gcovr --gcov-executable=%s --root=%s --print-summary --xml-pretty --output=%s" \
                             % (self.gcov_executable, root_dir, coverage_report_file)
        elif report_type == "html":
            gcovr_command = "gcovr --gcov-executable=%s --root=%s --print-summary --html --html-details --output=%s" \
                             % (self.gcov_executable, root_dir, coverage_report_file)
        else:
            logger.error("%s is illegal coverage report format." % format)
            return False

        gcovr_args = shlex.split(gcovr_command)

        if settings['exclude_unreachable_branches']:
            gcovr_args.extend(["--exclude-unreachable-branches"])

        if settings['exclude_throw_branches']:
            gcovr_args.extend(["--exclude-throw-branches"])

        excludes.append(".*tests.*")
        excludes = ["--exclude=%s" % exclude.replace(root_dir, '').strip(os.path.sep) for exclude in excludes]

        filters = ["--filter=%s" % filter.strip(os.path.sep) for filter in filters]

        gcovr_args.extend(excludes)
        gcovr_args.extend(filters)
        try:
            return Command.execute_command(gcovr_args)
        except Exception as e:
            logger.exception("generate coverage report file with gcovr tool exception %s." % e)
            raise
