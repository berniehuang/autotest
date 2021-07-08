# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: jacoco_report.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.3.12
# ------------------------------------------------------------------------------
import os
import shlex
import logging
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import suntest.core.command as Command
from coverage_report import CoverageReport
from jacoco2cobertura import Jacoco2Cobertura

logger = logging.getLogger(__name__)

class JacocoReport(CoverageReport):
    def __init__(self, jacoco_reporter, report_type='xml'):
        self._jacoco_reporter = jacoco_reporter
        self._jacoco_report_command = ''
        self._report_type = report_type

    def generate_coverage_report(self):
        jacoco_args = shlex.split(self._jacoco_report_command)
        try:
            return Command.execute_command(jacoco_args)
        except Exception as e:
            logger.exception("generate coverage report file with jacoco tool exception %s." % e)
            raise

    def transfer_jacoco_2_cobertura(self, source_root, source_dirs, jacoco_coverage_report, cobertura_coverage_report):
        """
        Description:
            transfer jacoco coverage xml report 2 Cobertura coverage xml report.
        Return: (bool)
        Parameters:
            source_root: (str) source code directory.
            source_dirs: (list) source code directory for each junit.
            jacoco_coverage_report: (str) jacoco code coverage xml report.
            cobertura_coverage_report: (str) cobertura coverage xml report.
        """
        jacoco_2_cobertura = Jacoco2Cobertura(source_root, source_dirs, jacoco_coverage_report, cobertura_coverage_report)
        jacoco_2_cobertura.convert_jacoco_report_2_cobertura_report()

class JacocoAndroid9Report(JacocoReport):
    """
    For Android9 project.
    """
    def generate_coverage_report(self, classfiles, execution_files, source_dirs, report_dir):
        """
        Description:
            generate coverage report with jacoco for Android9.
        Parameters:
            classfiles: (list) classfile list.
            execution_files: (list) coverage ec filepath list.
            source_dirs: (list) source code directorys.
            report_dir: (str) coverage report output dir.
            report_type: (str) coverage report type, default type is xml.
        Return: (bool)
        """
        if self._report_type == 'xml':
            report = os.path.join(report_dir, 'report.xml')
        else:
            report = report_dir

        self._jacoco_report_command = "java -jar %s report --classfiles %s --%s %s %s %s" \
                         % (self._jacoco_reporter, classfiles[0], self._report_type, report, \
                         ' '.join(["--sourcefiles %s" % source_dir for source_dir in source_dirs]), \
                         ' '.join(["%s" % execution_file for execution_file in execution_files]))
        super(JacocoAndroid9Report, self).generate_coverage_report()

class JacocoAndroid8Report(JacocoReport):
    """
    For Android8 project.
    """
    def generate_coverage_report(self, metadata_files, execution_files, source_dirs, report_dir):
        """
        Description:
            generate coverage report with jacoco for Android8.
        Parameters:
            metadata_file: (list) coverage em files.
            execution_file: (str) coverage ec filepath.
            source_dir: (str) source code directory.
            report_dir: (str) coverage report ouput dir.
            report_type: (str) coverage report type, default type is xml.
        Return: (bool)
        """
        self._jacoco_report_command = "java -jar %s --metadata-file %s %s %s --report-type %s --report-dir %s" \
                         % (self._jacoco_reporter, metadata_files[0],
                         ' '.join(["--coverage-file %s" % execution_file for execution_file in execution_files]), \
                         ' '.join(["--source-dir %s" % source_dir for source_dir in source_dirs]), \
                         self._report_type, report_dir)
        super(JacocoAndroid8Report, self).generate_coverage_report()

class JacocoReportFactory(object):
    operator = {
        'Android8': JacocoAndroid8Report,
        'Android9': JacocoAndroid9Report
    }

    @staticmethod
    def get_jacoco_report(android_version, jacoco_reporter, report_type):
        return JacocoReportFactory.operator.get(android_version)(jacoco_reporter, report_type)
