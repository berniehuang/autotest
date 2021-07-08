# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: unittest_result.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.12.15
# Input:
#      None
# ------------------------------------------------------------------------------
from coverage_info import CoverageInfo
from result_info import ResultInfo
from suntest import ExitStatus


class UnitTestResult(object):
    def __init__(self):
        self.coverage = CoverageInfo()
        self.result = ResultInfo()
        self.flag = ExitStatus.OK

    def __str__(self):
        return """[测试用例总数]: %(cases)s
[测试用例失败数]: %(failures)s
[测试用例错误数]: %(errors)s
[行覆盖率]: %(line_rate)s
[行覆盖数]: %(line_cover)s
[行总数]: %(line_total)s
[分支覆盖率]: %(branch_rate)s
[分支覆盖数]: %(branch_cover)s
[分支总数]: %(branch_total)s""" % dict(
                                            cases=str(self.result.cases),
                                            failures=str(self.result.failures),
                                            errors=str(self.result.errors),
                                            line_rate=str(self.coverage.line_coverage.line_rate),
                                            line_cover=str(self.coverage.line_coverage.line_cover),
                                            line_total=str(self.coverage.line_coverage.line_total),
                                            branch_rate=str(self.coverage.branch_coverage.branch_rate),
                                            branch_cover=str(self.coverage.branch_coverage.branch_cover),
                                            branch_total=str(self.coverage.branch_coverage.branch_total))

    @property
    def test_cases(self):
        return str(self.result.cases)

    @property
    def test_failures(self):
        return str(self.result.failures)

    @property
    def line_rate(self):
        return str(self.coverage.line_coverage.line_rate)

    @property
    def line_cover(self):
        return str(self.coverage.line_coverage.line_cover)

    @property
    def line_total(self):
        return str(self.coverage.line_coverage.line_total)

    @property
    def branch_rate(self):
        return str(self.coverage.branch_coverage.branch_rate)

    @property
    def branch_cover(self):
        return str(self.coverage.branch_coverage.branch_cover)

    @property
    def branch_total(self):
        return str(self.coverage.branch_coverage.branch_total)
