# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: testrunner.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import time
import logging

from suntest import ExitStatus
from suntest.core import exceptions
from suntest.config import settings

logger = logging.getLogger(__name__)


class EmuRunner(object):
    def __init__(self, test_config, device):
        self.test_result_flag = ExitStatus.OK
        self._type = str(test_config.get("type", ""))
        self.test_config = test_config
        self._device = device

    def __str__(self):
        return """[测试类型]: %(type)s
[检查状态]: device/offline
[检查进程]: %(process)s
[检查日志]: %(logline)s
[检查属性]: %(property)s""" % dict(
            type = str(self._type),
            process = str('\n            '.join([process for process in self.test_config.get("process_list", [])])),
            logline = str('\n            '.join([log for log in self.test_config.get("startup_log", [])])),
            property = str('\n            '.join([property.get("key") for property in self.test_config.get("property", [])])))

    @property
    def type(self):
        return self._type

    @property
    def device(self):
        return self._device

    def run(self):
        """
        Description:
            smoketest emulator startup.
        Return: (tool)
        """
        self.start_device()
        self.test_device_state()
        self.test_process_list()
        self.test_startup_log()
        self.test_get_property()
        self.stop_device()

        return self.test_result_flag

    def test_device_state(self):
        logger.info("设备启动状态检查...")

        if self.device.device_state == "device":
            logger.debug("设备状态测试成功.")
            return True
        else:
            logger.error("设备状态测试失败: %s" % self.device.device_state)
            self.test_result_flag = ExitStatus.DEVICE_STATE_OFFLINE
            return False

    def test_process_list(self):
        logger.info("设备启动进程检查...")

        for process in self.test_config.get("process_list", []):
            if process not in self.device.get_process_list():
                logger.error("设备进程列表中没有%s" % process)
                self.test_result_flag = ExitStatus.DEVICE_PROCESS_LACK
                return False

        logger.debug("设备进程列表中包含所有检查进程.")
        return True

    def test_startup_log(self):
        logger.info("设备启动日志检查...")

        with open(self.device.device_log_file, 'r') as f:
            device_startup_logs = [startup_log.strip('\n') for startup_log in f.readlines()]
            for log in self.test_config.get("startup_log", []):
                if log not in device_startup_logs:
                    logger.error("设备启动日志中没有'%s'" % log)
                    self.test_result_flag = ExitStatus.DEVICE_LOG_LACK
                    return False

        logger.debug("设备启动日志中包含所有检查日志.")
        return True

    def test_get_property(self):
        logger.info("设备启动属性检查...")

        for prop in self.test_config.get("property", []):
            if prop.get("value") != self.device.get_property(prop.get("key")).strip("\n"):
                logger.error("设备启动属性错误%s" % prop.get("key"))
                self.test_result_flag = ExitStatus.DEVICE_PROP_ERROR
                return False

        logger.debug("设备启动属性全部正确.")
        return True

    def start_device(self):
        """
        Description:
            startup device.
        """
        try:
            self._device.startup_device()
            if not self._device.check_device_startup():
                self._device.reboot_device()
        except exceptions.DeviceStartupFailure as e:
            raise e

    def stop_device(self):
        """
        Description:
            stop device.
        """
        self._device.stop_device()

