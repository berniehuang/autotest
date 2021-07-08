# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: result_report.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import re
import xmltodict
import collections
import logging
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from suntest.config import settings
from xml.dom.minidom import parseString

logger = logging.getLogger(__name__)


class ResultReport(object):
    def __init__(self):
        self._gtest_result_report = None
        self._qtest_result_report = None
        self._junit_result_report = None

    def set_gtest_result_report(self, gtest_result_report):
        self._gtest_result_report = gtest_result_report

    def set_junit_result_report(self, junit_result_report):
        self._junit_result_report = junit_result_report

    def set_qtest_result_report(self, qtest_result_report):
        self._qtest_result_report = qtest_result_report

    @property
    def gtest_result_report(self):
        return self._gtest_result_report

    @property
    def qtest_result_report(self):
        return self._qtest_result_report

    @property
    def junit_result_report(self):
        return self._junit_result_report

    def parse_junit_result_report(self, result_report):
        """
        Description:
            parse junit result report to get result data.
        Return: (list) the tests and failures of the unittest report
        """
        _tests = 0
        _failures = 0

        try:
            tree = ET.parse(result_report)
            root = tree.getroot()
            _tests = int(root.get('tests'))
            _failures = int(root.get('failures'))
        except IOError:
            logger.error("单体测试结果报告%s不存在。" % result_report)
        except Exception as e:
            logger.error("解析JUnit格式的单体测试结果报告发生异常: %s。" % e)
        finally:
            return (_tests, _failures)

    def parse_qt_result_report(self, result_report):
        """
        Description:
            parse qt result report to get result data.
        Return: (list) the tests and failures of the unittest report
        """
        _tests = 0
        _failures = 0

        try:
            tree = ET.parse(result_report)
            root = tree.getroot()
            failures_number = 0
            for incident in [testfunction.find("Incident") for testfunction in root.findall('TestFunction')]:
                if "failures" == incident.attrib.get('type'):
                    failures_number = failures_number + 1
            _failures = _failures + int(root.get('failures', failures_number))
            _tests = _tests + int(root.get('testobjects', len(root.findall('TestFunction'))))
        except IOError:
            logger.error("单体测试结果报告%s不存在。" % result_report)
        except Exception as e:
            logger.exception("解析Qt格式的单体测试结果报告发生异常: %s。" % e)
        finally:
            return (_tests, _failures)

    def combine_gtest_result_reports(self, xmllist):
        tests = failures = disabled = errors = time = 0
        name = str()
        testsuitesDicts = list()

        for readxmlstr in xmllist:
            xmlDict = xmltodict.parse(readxmlstr)
            testsuitesDict = xmlDict.get("testsuites")
            tests = tests + int(testsuitesDict.get("@tests"))
            failures = failures + int(testsuitesDict.get("@failures"))
            disabled = disabled + int(testsuitesDict.get("@disabled"))
            errors = errors + int(testsuitesDict.get("@errors"))
            time = time + float(testsuitesDict.get("@time"))
            name = testsuitesDict.get("@name")
            if isinstance(testsuitesDict.get("testsuite"), list):
                testsuitesDicts.extend(testsuitesDict.get("testsuite"))
            else:
                testsuitesDicts.append(testsuitesDict.get("testsuite"))

        testsuitesdict = collections.OrderedDict()
        testsuitesdict["@tests"] = tests
        testsuitesdict["@failures"] = failures
        testsuitesdict["@disabled"] = disabled
        testsuitesdict["@errors"] = errors
        testsuitesdict["@time"] = time
        testsuitesdict["@name"] = name
        testsuitesdict["testsuite"] = testsuitesDicts

        rootdict = collections.OrderedDict()
        rootdict["testsuites"] = testsuitesdict

        xmlstr = xmltodict.unparse(rootdict)

        return xmlstr

    def combine_qtest_result_reports(self, xmllist):
        """
        Description:
            combine mult qt result reports to one qt result report.
        Return: (str) the string of mult qt result xml
        """
        TestCaseDict = TestCasenameDict = EnvironmentDict = collections.OrderedDict()
        TestFunctionDicts = list()

        for readxmlstr in xmllist:
            xmlDict = xmltodict.parse(readxmlstr)
            TestCaseDict = xmlDict.get("TestCase")
            TestCasenameDict = TestCaseDict.get("@name")
            EnvironmentDict = TestCaseDict.get("Environment")
            TestFunctionDicts.extend(TestCaseDict.get("TestFunction"))

        testcasedict = collections.OrderedDict()
        testcasedict["@name"] = TestCasenameDict
        testcasedict["Environment"] = EnvironmentDict
        testcasedict["TestFunction"] = TestFunctionDicts

        rootdict = collections.OrderedDict()
        rootdict["TestCase"] = testcasedict

        xmlstr = xmltodict.unparse(rootdict)

        return xmlstr

    def combine_junit_result_reports(self, xmllist):
        tests = failures = time = 0
        name = str()
        testsuitesDicts = list()
        testsuiteDicts = list()

        for readxmlstr in xmllist:
            try:
                xmlDict = xmltodict.parse(readxmlstr)
                if isinstance(xmlDict.get("testsuite"), list):
                    testsuiteDicts.extend(xmlDict.get("testsuite"))
                else:
                    testsuiteDicts.append(xmlDict.get("testsuite"))
            except Exception as e:
                print e

        for testsuiteDict in testsuiteDicts:
            tests = tests + int(testsuiteDict.get("@tests"))
            failures = failures + int(testsuiteDict.get("@failures"))
            time = time + float(testsuiteDict.get("@time"))
            name = testsuiteDict.get("@name")

        testsuitesdict = collections.OrderedDict()
        testsuitesdict["@tests"] = tests
        testsuitesdict["@failures"] = failures
        testsuitesdict["@time"] = time
        testsuitesdict["@name"] = name
        testsuitesdict["testsuite"] = testsuiteDicts

        rootdict = collections.OrderedDict()
        rootdict["testsuites"] = testsuitesdict

        xmlstr = xmltodict.unparse(rootdict)

        return xmlstr

    def read_result_reports(self, test_result_reports):
        """
        Description:
            read mult xml result report to xmlstr.
        Return: (list) return list of readxmlstr
        """
        xmllist = list()

        for test_result_report in test_result_reports:
            try:
                with open(test_result_report) as f:
                    readxmlstr = f.read()
                    xmllist.append(readxmlstr)
            except IOError as e:
                logger.error("测试结果报告%s不存在。" % test_result_report)
                return xmllist

        return xmllist

    def write_result_report(self, xmlstr, result_report):
        """
        Description:
            write xml string in xml format result report.
        Return: (bool) if write result report success then reutrn true or false
        """
        dom = parseString(xmlstr)
        try:
            with open(result_report,'w') as f:
                dom.writexml(f, indent='', addindent='\t', newl='\n', encoding='UTF-8')
                return True
        except Exception as e:
            logger.exception("编写测试结果报告发生异常: %s\n" % str(e))
            return False
