# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: result_info.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------


class ResultInfo(object):
    def __init__(self):
        self.cases = 0
        self.failures = 0
        self.errors = 0

    def __str__(self):
        return """[cases]: %(cases)s
[failures]: %(failures)s
[errors]: %(errors)s""" % dict(
            cases=str(self.cases),
            failures=str(self.failures),
            errors=str(self.errors))

    def set(self, (cases, failures)):
        self.cases += int(cases)
        self.failures += int(failures)
