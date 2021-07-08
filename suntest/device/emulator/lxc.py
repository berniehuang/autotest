# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: lxc.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.9.26
# -------------------------------------------------------------------------------
import re
import os
import sys
import stat
import time
import shlex
import psutil
import signal
import getpass
import logging
import subprocess
from datetime import datetime
from distutils.spawn import find_executable

from suntest.core import exceptions
from suntest.core import process
from suntest.device.device import Device
from suntest.device.adb import ADB
from suntest.config import settings
import suntest.core.command as Command
import suntest.files.remove as Remove


logger = logging.getLogger(__name__)


class Lxc(Device):
    """ device type lxc
    """
    def __init__(self, **kwargs):
        super(Lxc, self).__init__(**kwargs)
        self.adb = ADB()
        self._adb_path = os.path.join(os.environ['%s_HOST_OUT' % settings.compile_arch], "bin/adb")
        if self._adb_path:
            self.adb.set_adb_path(self._adb_path)
            logger.debug("adb路径: %s" % self.adb.get_adb_path())
            self.adb.restart_server()
            logger.debug("adb版本: %s" % self.adb.get_version())
        self.device_log_file = "device.log"
        self.log_fd = open(self.device_log_file, 'w')

    def startup_device(self):
        """
        Description:
            startup the specify lxc
        Return: (bool)
        """


        start_anbox_session_manager = "./build/lxc.sh session-manager-start"
        startup_lxc_command = "./build/lxc.sh start"
        if settings.simulator=="true":
            startup_lxc_command = "sudo simulator --path ./ --start"
        logger.debug("启动lxc命令: %s" % startup_lxc_command)
        startup_lxc_args = shlex.split(startup_lxc_command)

        try:
            subprocess.Popen(start_anbox_session_manager, shell=True,stdout=self.log_fd, stderr=self.log_fd)
            self.log_fd.flush()
        except Exception as e:
            logger.exception("启动session-manager服务发生异常:  %s." % e)
            raise
        logger.info("启动session-manager服务成功")

        try:
            subprocess.Popen(startup_lxc_args, stdout=self.log_fd, stderr=self.log_fd)
            self.log_fd.flush()
        except Exception as e:
            logger.exception("启动模拟器发生异常:  %s." % e)
            raise

    def stop_device(self):
        """
        Description:
            stop the specify device
        Return: (bool)
        """
        stop_lxc_command = "./build/lxc.sh stop"
        if settings.simulator=="true":
            stop_lxc_command = "sudo simulator --path ./ --stop"
        stop_lxc_args = shlex.split(stop_lxc_command)

        try:
            subprocess.Popen(stop_lxc_args, stdout=self.log_fd, stderr=self.log_fd)
        except OSError as e:
            logger.exception("关闭模拟器异常。")
            raise
        logger.info("关闭模拟器成功。")

        return True

    def check_device_startup(self, times=3):
        """
        Description:
            check up device if or not start up.
        Return: (bool)
        Parameter: times (int)
        """
        lxc_info_command = "./build/lxc.sh info"
        if settings.simulator=="true":
            lxc_info_command = "sudo simulator --path ./ --info"
        lxc_info_args = shlex.split(lxc_info_command)

        check_times = 1

        while check_times <= times:
            get_inc_info = subprocess.Popen(lxc_info_args , stdout=subprocess.PIPE)
            lxc_info = get_inc_info.stdout.readlines()
            for lxc_info_line in lxc_info:
                check = lxc_info_line.split(' ')[0].strip()
                if check != "IP:":
                    continue
                IP = lxc_info_line.split(':')[1].strip()
                logger.info("模拟器IP：%s."%IP)
                self.adb.connect_remote(IP)

            logger.debug("检查模拟器设备状态第%s次。" % check_times)
            check_times = check_times + 1
            self.adb.wait_for_device()
            return_code = self.adb.get_return_code()
            if return_code == 0:
                if self.device_state == "device":
                    logger.info("模拟器设备状态： %s." % self.device_state)
                    return True
                else:
                    logger.warning("模拟器设备状态： %s." % self.device_state)
                    self.adb.kill_server()
                    continue
            else:
                logger.warning("检查模拟器设备状态失败。返回码:[%d]." % return_code)
                time.sleep(5)
                continue

        logger.error("启动模拟器失败。")
        return False

    def reboot_device(self, times=3):
        """
        Description:
            reboot the specify device for 3 times.
        Return: (bool)
        """
        reboot_times = 1

        while reboot_times <= times:
            self.startup_device()
            if not self.check_device_startup():
                logger.warning("重启模拟器设备失败第%d次。" % reboot_times)
                reboot_times = reboot_times + 1
                time.sleep(5)
                continue
            else:
                logger.info("重启模拟器设备成功。")
                return True

        try:
            with open(self.device_log_file, 'r') as f:
                print 110 * "="
                print 50 * " " + "--设备启动日志--"
                for line in f.readlines():
                    print line.strip('\n')
                print 110 * "="
        except IOError:
            logger.exception("%s不存在。" % self.device_log_file)

        raise exceptions.DeviceStartupFailure("重启模拟器三次失败，停止运行单体测试")

    def get_property(self):
        """
        Description:
            get property from device.
        Return: (dict) property from device
        """
        get_property_command = "getprop"
        get_property_args = [self._adb_path, "-s", self.serial_number, "shell", get_property_command]

        try:
            p_get_property = subprocess.Popen(get_property_args, stdout=subprocess.PIPE)
            property_lines = p_get_property.stdout.readlines()
            for property_line in property_lines:
                key = property_line.split(':')[0].replace('[', '').replace(']', '')
                value = property_line.split(':')[1].strip('\r\n').strip().replace('[', '').replace(']', '')
                self._property[key] = value
            return self._property
        except Exception as e:
            logger.exception("get property exception %s." % e)
            raise

    def __del__(self):
        self.log_fd.close()
