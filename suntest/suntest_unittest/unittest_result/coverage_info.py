# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: coverage_info.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------


class LineInfo(object):
    def __init__(self):
        self.line_rate = 0
        self.line_cover = 0
        self.line_total = 0


class BranchInfo(object):
    def __init__(self):
        self.branch_rate = 0
        self.branch_cover = 0
        self.branch_total = 0


class CoverageInfo(object):
    def __init__(self):
        self.line_coverage = LineInfo()
        self.branch_coverage = BranchInfo()

    def __str__(self):
        return """[line_rate]: %(line_rate)s
[line_cover]: %(line_cover)s
[line_total]: %(line_total)s
[branch_rate]: %(branch_rate)s
[branch_cover]: %(branch_cover)s
[branch_total]: %(branch_total)s""" % dict(
            line_rate=str(self.line_coverage.line_rate),
            line_cover=str(self.line_coverage.line_cover),
            line_total=str(self.line_coverage.line_total),
            branch_rate=str(self.branch_coverage.branch_rate),
            branch_cover=str(self.branch_coverage.branch_cover),
            branch_total=str(self.branch_coverage.branch_total))

    def set(self, (line_rate, line_cover, line_total, branch_rate, branch_cover, branch_total)):
        self.line_coverage.line_cover += int(line_cover)
        self.line_coverage.line_total += int(line_total)
        try:
            self.line_coverage.line_rate = "%.2f%%" % float(100 * float(self.line_coverage.line_cover)/float(self.line_coverage.line_total))
        except ZeroDivisionError as e:
            self.branch_coverage.line_rate = "0%"
        self.branch_coverage.branch_cover += int(branch_cover)
        self.branch_coverage.branch_total += int(branch_total)
        try:
            self.branch_coverage.branch_rate = "%.2f%%" % float(100 * float(self.branch_coverage.branch_cover)/float(self.branch_coverage.branch_total))
        except ZeroDivisionError as e:
            self.branch_coverage.branch_rate = "0%"
