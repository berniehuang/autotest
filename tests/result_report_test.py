import os
import unittest
import suntest.files.remove as Remove
from suntest.suntest_unittest.report.result_report import ResultReport

class TestResultReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result_report_data_path = os.path.join(os.path.realpath(__file__).split("result_report_test.py")[0], "data/result_report")

    @classmethod
    def tearDownClass(cls):
        #Remove.remove_all_files(cls.result_report_data_path)
        pass

    def setUp(self):
        self.result_report = ResultReport()
        self.junit_result_xmlstr = '''<?xml version="1.0" encoding="UTF-8"?>
<testsuites tests="1" failures="0" disabled="0" errors="0" time="19700101090024.000000" name="Alltests">
  <testsuite name="Test_Sample" tests="1" failures="0" disabled="0" errors="0" time="0.02">
    <testcase name="case_demo" status="run" time="0.01" classname="Test_Sample">
    </testcase>
  </testsuite>
</testsuites>
'''
        self.qt_result_xmlstr = '''<?xml version="1.0" encoding="UTF-8"?>
<TestCase name="TestQString">
<Environment>
    <QtVersion>5.2.1</QtVersion>
    <QTestVersion>5.2.1</QTestVersion>
</Environment>
<TestFunction name="initTestCase">
<Incident type="pass" file="" line="0" />
</TestFunction>
<TestFunction name="cleanupTestCase">
<Incident type="pass" file="" line="0" />
</TestFunction>
</TestCase>
'''

    def tearDown(self):
        del self.result_report

    def test_set_gtest_result_report(self):
        gtest_result_report = "gtest_result.xml"
        self.result_report.set_gtest_result_report(gtest_result_report)
        self.assertEqual(gtest_result_report, self.result_report.gtest_result_report)

    def test_set_qtest_result_report(self):
        qtest_result_report = "qtest_result.xml"
        self.result_report.set_qtest_result_report(qtest_result_report)
        self.assertEqual(qtest_result_report, self.result_report.qtest_result_report)

    def test_parse_junit_result_report(self):
        junit_result_report = os.path.join(TestResultReport.result_report_data_path, "gtest-result-demo.xml")

        (tests, failures) = self.result_report.parse_junit_result_report(junit_result_report)
        self.assertEqual((10, 6), (tests, failures))

    def test_parse_qt_result_report(self):
        qtest_result_report = os.path.join(TestResultReport.result_report_data_path, "qtest-result-demo.xml")

        (tests, failures) = self.result_report.parse_qt_result_report(qtest_result_report)
        self.assertEqual((3, 0), (tests, failures))

    def test_read_junit_result_reports(self):
        junit_result_reports = [os.path.join(TestResultReport.result_report_data_path, "gtest-result-simple.xml")]
        readxmlStrs = self.result_report.read_result_reports(junit_result_reports)
        self.assertEqual([self.junit_result_xmlstr], readxmlStrs)

    def test_read_qt_result_reports(self):
        qt_result_reports = [os.path.join(TestResultReport.result_report_data_path, "qtest-result-simple.xml")]
        readxmlStrs = self.result_report.read_result_reports(qt_result_reports)
        self.assertEqual([self.qt_result_xmlstr], readxmlStrs)

    def test_write_junit_result_report(self):
        test_result_report = "junit-result-demo.xml"
        self.assertTrue(self.result_report.write_result_report(self.junit_result_xmlstr, test_result_report))

    def test_write_qt_result_report(self):
        test_result_report = "qt-result-demo.xml"
        self.assertTrue(self.result_report.write_result_report(self.qt_result_xmlstr, test_result_report))

    def test_combine_gtest_result_reports(self):
        gtest_result_reports = [os.path.join(TestResultReport.result_report_data_path, "gtest-result-demo.xml"), \
                                os.path.join(TestResultReport.result_report_data_path, "gtest-result-simple.xml")]
        readxmlStrs = self.result_report.read_result_reports(gtest_result_reports)
        xmlStr = self.result_report.combine_gtest_result_reports(readxmlStrs)

    def test_combine_qtest_result_reports(self):
        qtest_result_reports = [os.path.join(TestResultReport.result_report_data_path, "qtest-result-demo.xml"), \
                                os.path.join(TestResultReport.result_report_data_path, "qtest-result-simple.xml")]
        readxmlStrs = self.result_report.read_result_reports(qtest_result_reports)
        xmlStr = self.result_report.combine_qtest_result_reports(readxmlStrs)
