# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: emulator.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
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


class Emulator(Device):
    """ device type emulator
    """
    def __init__(self, **kwargs):
        super(Emulator, self).__init__(**kwargs)
        self._emu_path = None
        self._process_info = None
        self._property = dict()
        self.adb = ADB()
        self.virtual_xserver = kwargs.get("virtual_xserver")
        self.device_log_file = os.path.join(settings.workspace, "device.log")
        self.log_fd = open(self.device_log_file, 'w')
        self.logcat = kwargs.get("logcat")
        self.emulator_home = kwargs.get("emulator_home")

    @property
    def process_info(self):
        return self._process_info

    def checkup_emulator_env(self, emulator_process_name):
        """
        Description:
            checkup and clear temporarily emulator files
        Return: (bool)
        """
        if self._adb_path:
            self.adb.set_adb_path(self._adb_path)
            logger.debug("adb路径: %s" % self.adb.get_adb_path())
            self.adb.restart_server()
            logger.debug("adb版本: %s" % self.adb.get_version())

        pids = process.get_pid_list(emulator_process_name)
        if pids:
            for pid in pids:
                try:
                    logger.debug("杀死模拟器进程id: %d" % pid)
                    os.kill(pid, signal.SIGKILL)
                except OSError as e:
                    logger.exception("没有找到这个进程。")

        if self.adb.get_devices():
            print self.devices_list
            # raise exceptions.MorethanOneDevice("more than one device.")

        nutshell_file_path = "/tmp/nutshell-%s" % getpass.getuser()
        if os.path.isdir(nutshell_file_path):
            temp_emulators = os.listdir(nutshell_file_path)
            if temp_emulators:
                return Remove.remove_all_files(nutshell_file_path)

    def startup_device(self, startup_emulator_command, emulator_process_name):
        """
        Description:
            startup the specify emulator
        Return: (bool)
        """
        self.checkup_emulator_env(emulator_process_name)

        startup_emulator_shell=str()
        virtual_xserver_command = "xvfb-run --auto-servernum --server-args=\"-screen 0 1280x760x24\""

        logger.info("正在启动模拟器...")
        logger.debug("启动模拟器命令: %s" % startup_emulator_command)
        if (self.virtual_xserver == "on" and find_executable("xvfb-run")) or (self.emulator_home):
            try:
                startup_emulator_shell = "/tmp/startup_emu.sh"
                with open(startup_emulator_shell, 'w+') as f:
                    f.write(startup_emulator_command)
                    os.chmod(startup_emulator_shell, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
            except Exception as e:
                logger.error("Caught unexpected exception: %s\n" % str(e))
                return False

        if self.virtual_xserver == "on" and find_executable("xvfb-run"):
            startup_emulator_command = "%s %s" % (virtual_xserver_command, startup_emulator_shell)
            logger.debug("虚拟屏幕启动模拟器命令: %s" % startup_emulator_command)

        if not self.emulator_home:
            startup_emulator_args = shlex.split(startup_emulator_command)
            try:
                p_startup_emulator = subprocess.Popen(startup_emulator_args, stdout=self.log_fd, stderr=self.log_fd)
                self.log_fd.flush()
                self._process_info = psutil.Process(p_startup_emulator.pid)
            except Exception as e:
                logger.exception("启动模拟器发生异常:  %s." % e)
                raise
        else:
            startup_emulator_shell = str(startup_emulator_command)
            try:
                p_startup_emulator = subprocess.Popen(startup_emulator_shell, shell=True, stdout=self.log_fd, stderr=self.log_fd)
                self.log_fd.flush()
                self._process_info = psutil.Process(p_startup_emulator.pid)
            except Exception as e:
                logger.exception("启动模拟器发生异常: %s." % e)
                raise

    def stop_device(self):
        """
        Description:
            stop the specify device
        Return: (bool)
        """
        self.adb.run_emulator("kill")
        return_code = self.adb.get_return_code()
        if return_code == 0:
            if self.adb.get_devices():
                logger.info("adb device列表如下: %s" % self.adb.get_devices())
                pids = process.get_pid_list(settings.emulator_process_name)
                if pids:
                    for pid in pids:
                        try:
                            logger.debug("杀死模拟器进程id: %d" % pid)
                            os.kill(pid, signal.SIGKILL)
                        except OSError as e:
                            logger.exception("没有找到这个进程。")
                return False
            else:
                logger.info("关闭模拟器成功。")
                return True
        else:
            logger.error("关闭模拟器失败。")
            return False

    def check_device_startup(self, times=3):
        """
        Description:
            check up device if or not start up.
        Return: (bool)
        Parameter: times (int)
        """
        check_times = 1

        while check_times <= times:
            logger.debug("检查模拟器设备状态第%s次。" % check_times)
            check_times = check_times + 1
            self.adb.wait_for_device()
            return_code = self.adb.get_return_code()
            if return_code == 0:
                if self.device_state == "device":
                    logger.info("模拟器设备状态： %s." % self.device_state)
                    time.sleep(20)
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

    def __del__(self):
        self.log_fd.close()
