# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Filename: anbox.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.9.26
# ------------------------------------------------------------------------------
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


class Anbox(Device):
    """ device type anbox
    """
    def __init__(self, **kwargs):
        super(Anbox, self).__init__(**kwargs)
        self.adb = ADB()
        self._adb_path = os.path.join(os.environ['%s_HOST_OUT' % settings.compile_arch], "bin/adb")
        if self._adb_path:
            self.adb.set_adb_path(self._adb_path)
            logger.debug("adb path: %s" % self.adb.get_adb_path())
            self.adb.restart_server()
            logger.debug("Adb version: %s" % self.adb.get_version())
        device_log_file = "device-%s.log" % datetime.strftime(datetime.now(), format='%Y-%m-%d-%H:%M')
        self.log_fd = open(device_log_file, 'w')


    def startup_device(self):
        """
        Description:
            startup the specify anbox
        Return: (bool)
        """
        start_anbox_service = "sudo systemctl start anbox-container-manager"
        check_anbox_service = "systemctl status anbox-container-manager"
        startup_anbox_command = "anbox session-manager"
        check_anbox_service_args = shlex.split(check_anbox_service)

        times = 3
        check_times = 1
        while check_times <= times:
            os.system(start_anbox_service)
            get_service_info = subprocess.Popen(check_anbox_service_args, stdout=subprocess.PIPE)
            service_info = get_service_info.stdout.read()
            status = re.findall("running",service_info)
            if status:
                logger.info("%s success."%start_anbox_service)
                break
            else:
                if check_times == 3:
                    logger.info("%s fail."%start_anbox_service)
                    return False


        logger.debug("startup anbox command: %s" % startup_anbox_command)

        startup_anbox_args = shlex.split(startup_anbox_command)
        try:
            subprocess.Popen(startup_anbox_args, stdout=self.log_fd, stderr=self.log_fd)
        except Exception as e:
            logger.exception("startup anbox exception %s." % e)
            raise

    def stop_device(self):
        """
        Description:
            stop the specify device
        Return: (bool)
        """
        stop_anbox_service = "sudo systemctl stop anbox-container-manager"
        check_anbox_service = "systemctl status anbox-container-manager"
        check_anbox_service_args = shlex.split(check_anbox_service)

        times = 3
        check_times = 1
        while check_times <= times:
            os.system(stop_anbox_service)
            get_service_info = subprocess.Popen(check_anbox_service_args, stdout=subprocess.PIPE)
            service_info = get_service_info.stdout.read()
            status = re.findall("inactive",service_info)
            if status:
                logger.info("%s success."%stop_anbox_service)
                break
            else:
                if check_times == 3:
                    logger.info("%s fail."%stop_anbox_service)
                    return False
        return True

    def check_device_startup(self, times=3):
        """
        Description:
            check up device if or not start up.
        Return: (bool)
        Parameter: times (int)
        """
        check_times = 1

        while check_times <= times:
            logger.debug("check device startup %s times." % check_times)
            check_times = check_times + 1
            self.adb.wait_for_device()
            return_code = self.adb.get_return_code()
            if return_code == 0:
                if self.device_state == "device":
                    logger.info("device state is %s." % self.device_state)
                    return True
                else:
                    logger.warning("device state is %s." % self.device_state)
                    self.adb.kill_server()
                    continue
            else:
                logger.warning("check if device startup returncode %d for %d times." % (return_code, check_times))
                time.sleep(5)
                continue

        logger.error("startup device failure.")
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
                logger.warning("reboot device failed for %d times." % reboot_times)
                reboot_times = reboot_times + 1
                time.sleep(5)
                continue
            else:
                logger.info("reboot device successful.")
                return True

        raise exceptions.DeviceStartupFailure("startup device failure for %d times." % times)

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