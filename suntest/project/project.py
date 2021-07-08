# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: project.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
from suntest import ExitStatus


class Project(object):
    """
    Management object of test suites
        interface implemented by concrete impls
    """
    def __init__(self, name=None, workspace=None, device=None, config=None, tasks=None):
        """
            a project manage unittest how to run.
            Parameters:
                name: (str) the project name.
                workspace: (str) the project workspace include datas and builds.
                device: (Device) the device object.
                status: (str) the project status.
        """
        self.name = name
        self.workspace = workspace
        self.device = device
        self.result = ExitStatus.OK

    def add(self, data):
        """
        add test
        interface implemented by concrete impls
        """
        raise NotImplementedError

    def run(self, test):
        """
        run program
        interface implemented by concrete impls
        """
        raise NotImplementedError

    def build(self):
        """
        build a unittest process
        interface implemented by concrete impls
        """
        raise NotImplementedError
