# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: qtapptestrunner.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import sys
import time
import select
import subprocess
import logging

from testrunner import TestRunner
from suntest.core import exceptions
from suntest.suntest_unittest.coverage.gcov import Gcov
import suntest.core.command as Command

logger = logging.getLogger(__name__)


class QtApptestRunner(TestRunner):
    def __init__(self, test_config, device):
        super(QtApptestRunner, self).__init__(test_config, device)

    def clear_system_app_package(self):
        """
        Description:
            clear system app package on device.
        Return: (bool)
        Parameters:
            install_app_package_command: (str) install app package command.
        """
        logger.info("清理系统分区已安装包... ")
        clear_system_app_package_command = "rm -rf /system/apps"
        clear_system_app_package_args = [self._device._adb_path, "-s", self._device.serial_number, "shell", clear_system_app_package_command]
        if not Command.execute_command(clear_system_app_package_args, timeout=600):
            logger.error("清理系统分区已安装包失败。")

    def install_app_package(self, package):
        """
        Description:
            install app package on device.
        Return: (bool)
        Parameters:
            install_app_package_command: (str) install app package command.
        """
        packagemanager_status = self._device.get_property('init.svc.packagemanager')
        logger.debug("packagemanager status:[%s]" % packagemanager_status)

        logger.info("正在安装包%s... " % package)
        install_app_package_command = "cpki -fi /data/lib/%s" % (package)
        install_app_package_args = [self._device._adb_path, "-s", self._device.serial_number, "shell", install_app_package_command]
        if not Command.execute_command(install_app_package_args, timeout=600):
            logger.error("在设备上安装包%s失败" % self._test_library_files[0].name)
            raise exceptions.InstallAppPackageFailure(self._test_case_file.name)

    def execute_testcase(self, result_report):
        """
        Description:
            execute google test program on device.
        Return: (bool)
        Parameters:
            result_report: (str) the googletest result report.
        """
        _QtUI_test_timeout = 3600
        _caseoutput_timeout = 300

        self.clear_system_app_package()
        self.install_app_package(self._test_library_files[0].name)

        application_name = "%s/test/apptest.so" % (self._test_library_files[0]._application_path)

        run_QtUI_test_command = "cd /tmp/;%s %s %s -xml -o %s" % (self._set_env, self._test_case_file.name, application_name, os.path.join("/data", result_report))
        logger.debug("运行QtUI测试程序命令: %s" % run_QtUI_test_command)
        run_QtUI_test_args = [self._device._adb_path, "-s", self._device.serial_number, "shell", run_QtUI_test_command]
        try:
            logger.info("开始运行QtUI测试用例...")
            p_run_QtUI_test = subprocess.Popen(run_QtUI_test_args, stdout=subprocess.PIPE)
            timeout = _QtUI_test_timeout
            while True:
                while_begin = time.time()
                fd_set = select.select([p_run_QtUI_test.stdout], [], [], _caseoutput_timeout)
                if p_run_QtUI_test.stdout in fd_set[0]:
                    logline = p_run_QtUI_test.stdout.readline()
                    if logline:
                        try:
                            sys.stdout.write(logline)
                            sys.stdout.flush()
                        except IOError as e:
                            logger.exception("运行QtUI测试程序发生异常:%s." % e)
                            time.sleep(1)
                            continue
                        if "Segmentation fault" in logline:
                            p_run_QtUI_test.kill()
                            raise exceptions.SegmentationFault(self._test_case_file.name)
                    else:
                        if p_run_QtUI_test.poll() == None:
                            time.sleep(1)
                            continue
                        elif p_run_QtUI_test.poll() == 0:
                            logger.debug("QtUI测试程序返回码: (%d)." % p_run_QtUI_test.returncode)
                            break
                        else:
                            logger.error("QtUI测试程序返回码: (%d)." % p_run_QtUI_test.returncode)
                            break
                else:
                    p_run_QtUI_test.kill()
                    raise exceptions.OutputTimeout(_caseoutput_timeout)
                _QtUI_test_timeout = _QtUI_test_timeout - (time.time() - while_begin)
                if _QtUI_test_timeout <= 0:
                    p_run_QtUI_test.kill()
                    raise exceptions.RuncaseTimeout(_QtUI_test_timeout)
        except OSError:
            logger.exception("运行QtUI测试程序发生异常:%s." % e)
            raise
