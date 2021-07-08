# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: taskstate.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import logging
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError

logger = logging.getLogger(__name__)


class TasksState(object):
    """
    Management state of task in project
        interface implemented by concrete impls
    """
    NG = "NG"
    OK = "OK"
    FA = "FA"
    tasks_state_file = "tasks_state.ini"

    @staticmethod
    def initial_tasks_state(force_init, build_tasks):
        if force_init or not os.path.exists(TasksState.tasks_state_file):
            try:
                config = ConfigParser()
                config.add_section("unittest")
                for task in build_tasks:
                    if task == "emulator":
                        config.set("unittest", task, TasksState.OK)
                        continue
                    config.set("unittest", task, TasksState.NG)
            except NoSectionError as e:
                logger.exception("There is %s in tasks state file %s." % (e, TasksState.tasks_state_file))
                raise
            except Exception as e:
                logger.exception("load tasks state file error.")
                raise
            finally:
                config.write(open(TasksState.tasks_state_file, 'w+'))

    @staticmethod
    def notify_task_done(task):
        try:
            config = ConfigParser()
            config.read(TasksState.tasks_state_file)
            config.set("unittest", task, TasksState.OK)
            if task == "clean":
                config.set("unittest", "compile", TasksState.NG)
        except NoSectionError as e:
            logger.exception("There is %s in tasks state file %s." % (e, TasksState.tasks_state_file))
            raise
        except Exception as e:
            logger.exception("load tasks state file error.")
            raise
        finally:
            config.write(open(TasksState.tasks_state_file, 'w'))

    @staticmethod
    def notify_task_fail(task):
        try:
            config = ConfigParser()
            config.read(TasksState.tasks_state_file)
            config.set("unittest", task, TasksState.FA)
        except NoSectionError as e:
            logger.exception("There is %s in tasks state file %s." % (e, TasksState.tasks_state_file))
            raise
        except Exception as e:
            logger.exception("load tasks state file error.")
            raise
        finally:
            config.write(open(TasksState.tasks_state_file, 'w'))

    @staticmethod
    def get_task_state(task):
        try:
            config = ConfigParser()
            config.read(TasksState.tasks_state_file)
            flag = config.get("unittest", task)
            return flag
        except NoSectionError as e:
            logger.exception("There is %s in tasks state file %s." % (e, TasksState.tasks_state_file))
            raise
        except Exception as e:
            logger.exception("load tasks state file error.")
            raise
