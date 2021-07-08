# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: task.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import logging
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError

from taskstate import TasksState

logger = logging.getLogger(__name__)


class Task(object):
    """
    Management object of task in project
        interface implemented by concrete impls
    """
    def __init__(self, name="", actions=list(), dependon=None):
        """
            a task manage actions.
            Parameters:
                name: (str) the task name.
                actions: (list) a set of actions to achive task.
                dependon: (Task) the task depend on another task.
                state: (str) the task state.
        """
        self.name = name
        self.actions = actions
        self.dependon = dependon

    def get_actions(self):
        return self.actions

    def get_state(self):
        return TasksState.get_task_state(self.name)
