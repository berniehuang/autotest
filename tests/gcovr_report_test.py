import os
import unittest
import suntest.files.remove as Remove
from suntest.suntest_unittest.report.gcovr_report import GcovrReport

class TestGcovrReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gcovr_report_data_path = os.path.join(os.path.realpath(__file__).split("gcovr_report_test.py")[0], "data/gcovr_report")

    @classmethod
    def tearDownClass(cls):
        #Remove.remove_all_files(cls.gcovr_report_data_path)
        pass

    def setUp(self):
        self.gcovr_report = GcovrReport("/usr/bin/gcov")

    def tearDown(self):
        del self.gcovr_report

    def test_parse_coverage_report(self):
        coverage_report_file = os.path.join(TestGcovrReport.gcovr_report_data_path, "test-gcov-demo.xml")
        self.assertEqual(('100.00%', '29', '29', '100.00%', '10', '10'), self.gcovr_report.parse_cobertura_coverage_report(coverage_report_file, report_type='xml'))

    def test_parse_coverage_report_no_exists(self):
        coverage_report_file = "test-gcov-noexists.xml"
        self.assertEqual((0, 0, 0, 0, 0, 0), self.gcovr_report.parse_cobertura_coverage_report(coverage_report_file, report_type='xml'))

    def test_generate_coverage_report_format_xml(self):
        coverage_report_file = "test-gcov-src.xml"
        root_dir = os.path.join(os.path.realpath(__file__).split("gcovr_report_test.py")[0], "data/gcovr_report/src")
        self.assertTrue(self.gcovr_report.generate_coverage_report(coverage_report_file, root_dir))

    def test_generate_coverage_report_format_html(self):
        coverage_report_file = "test-gcov-src.html"
        root_dir = os.path.join(os.path.realpath(__file__).split("gcovr_report_test.py")[0], "data/gcovr_report/src")
        self.assertTrue(self.gcovr_report.generate_coverage_report(coverage_report_file, root_dir, report_type='html'))

    def test_generate_coverage_report_format_illegal(self):
        coverage_report_file = "test-gcov-src.illegal"
        root_dir = os.path.join(os.path.realpath(__file__).split("gcovr_report_test.py")[0], "data/gcovr_report/src")
        self.assertFalse(self.gcovr_report.generate_coverage_report(coverage_report_file, root_dir, report_type='illegal'))
