# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: coverage_report.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import shlex
import logging
import xmltodict
import collections
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import suntest.core.command as Command
logger = logging.getLogger(__name__)


class CoverageReport(object):
    def __init__(self):
        self._cobertura_coverage_report = None

    def set_cobertura_coverage_report(self, cobertura_coverage_report):
        self._cobertura_coverage_report = cobertura_coverage_report

    @property
    def cobertura_coverage_report(self):
        return self._cobertura_coverage_report

    def parse_cobertura_coverage_report(self, cobertura_coverage_report, report_type):
        """
        Description:
            parse cobertura coverage report to get coverage data.
        Parameters:
            cobertura_coverage_report: (str) cobertura coverage report filename.
            report_type: (str) report file format.
        Return: (tuple) coverage data
        """
        __coverage_data = (0, 0, 0, 0, 0, 0)

        if not os.path.exists(cobertura_coverage_report):
            logger.error("%s不存在." % cobertura_coverage_report)
            return __coverage_data

        if report_type == "xml":
            tree = ET.parse(cobertura_coverage_report)
            root = tree.getroot()
            try:
                branch_rate = "%.2f%%" % (float(root.get('branch-rate'))*100)
                branch_covered = "%d" % (int(root.get('branches-covered', 0)))
                branch_valid = "%d" % (int(root.get('branches-valid', 0)))
                line_rate = "%.2f%%" % (float(root.get('line-rate'))*100)
                line_covered = "%d" % (int(root.get('lines-covered', 0)))
                line_valid = "%d" % (int(root.get('lines-valid', 0)))
                __coverage_data = (line_rate, line_covered, line_valid, branch_rate, branch_covered, branch_valid)
            except Exception as e:
                logger.exception("解析覆盖率报告发生异常: %s." % e)
            finally:
                return __coverage_data
        else:
            return __coverage_data

    def combine_cobertura_coverage_reports(self, xmllist):
        lines_valid = lines_covered = branches_valid = branches_covered = complexity = 0
        sourcesDict = collections.OrderedDict()
        packageDicts = list()

        for readxmlstr in xmllist:
            xmlDict = xmltodict.parse(readxmlstr)
            coverageDict = xmlDict.get("coverage")
            lines_valid += int(coverageDict["@lines-valid"])
            lines_covered += int(coverageDict["@lines-covered"])
            branches_valid += int(coverageDict["@branches-valid"])
            branches_covered += int(coverageDict["@branches-covered"])
            complexity += float(coverageDict["@complexity"])
            sourcesDict = coverageDict.get("sources")
            packagesDict = coverageDict.get("packages")
            if packagesDict:
                if isinstance(packagesDict.get("package"), list):
                    packageDicts.extend(packagesDict.get("package"))
                else:
                    packageDicts.append(packagesDict.get("package"))

        packagesdict = collections.OrderedDict()
        packagesdict["package"] = packageDicts

        sourcesdict = sourcesDict

        try:
            coveragedict = collections.OrderedDict()
            coveragedict["@lines-covered"] = lines_covered
            coveragedict["@lines-valid"] = lines_valid
            coveragedict["@branches-covered"] = branches_covered
            coveragedict["@branches-valid"] = branches_valid
            coveragedict["@complexity"] = complexity
            coveragedict["@timestamp"] = 0
            coveragedict["sources"] = sourcesdict
            coveragedict["packages"] = packagesdict
            coveragedict["@line-rate"] = float(lines_covered) / float(lines_valid)
            coveragedict["@branch-rate"] = float(branches_covered) / float(branches_valid)
        except ZeroDivisionError as e:
            logger.error("覆盖率报告中统计的行总数或者分支总数为0.")
            coveragedict["@line-rate"] = float(0)
            coveragedict["@branch-rate"] = float(0)

        rootdict = collections.OrderedDict()
        rootdict["coverage"] = coveragedict

        xmlstr = xmltodict.unparse(rootdict)

        return xmlstr


    def read_cobertura_coverage_reports(self, cobertura_coverage_reports):
        """
        Description:
            read multi xml coverage report to xmlstr.
        Return: (list) return list of readxmlstr
        """
        xmllist = list()

        for cobertura_coverage_report in cobertura_coverage_reports:
            try:
                with open(cobertura_coverage_report) as f:
                    readxmlstr = f.read()
                    xmllist.append(readxmlstr)
            except IOError as e:
                logger.debug("%s不存在." % cobertura_coverage_report)
                continue
            except Exception as e:
                logger.exception("读取覆盖率报告发生异常: %s\n" % str(e))
                return xmllist

        return xmllist

    def write_cobertura_coverage_report(self, xmlstr, cobertura_coverage_report):
        """
        Description:
            write xml string in xml format coverage report.
        Return: (bool) if write result report success then reutrn true or false
        """
        dom = parseString(xmlstr)
        try:
            with open(cobertura_coverage_report,'w') as f:
                dom.writexml(f, indent='', addindent='\t', newl='\n', encoding='UTF-8')
                return True
        except Exception as e:
            logger.exception("编写覆盖率报告发生异常: %s\n" % str(e))
            return False

