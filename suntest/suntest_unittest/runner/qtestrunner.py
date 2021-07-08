# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: qtestrunner.py
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
import suntest.core.command as Command

logger = logging.getLogger(__name__)


class QtestRunner(TestRunner):
    def execute_testcase(self, result_report):
        """
        Description:
            execute Qt test program on device.
        Return: (bool)
        Parameters:
            result_report: (str) the googletest result report.
        """
        _qttest_timeout = 3600
        _caseoutput_timeout = 300

        run_qttest_command = "%s %s -o -,txt -o %s,xunitxml" % (self._set_env, self._test_case_file.name, os.path.join("data", result_report))
        logger.debug("运行Qt单体测试程序的命令: %s" % run_qttest_command)

        logger.info("开始运行Qt测试用例...")
        run_qttest_args = [self._device._adb_path, "-s", self._device.serial_number, "shell", run_qttest_command]
        try:
            p_run_qttest = subprocess.Popen(run_qttest_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                while_begin = time.time()
                fd_set = select.select([p_run_qttest.stdout, p_run_qttest.stderr], [], [], _caseoutput_timeout)
                if p_run_qttest.stdout in fd_set[0]:
                    logline = p_run_qttest.stdout.readline()
                    if logline:
                        try:
                            sys.stdout.write(logline)
                            sys.stdout.flush()
                        except IOError as e:
                            logger.exception("输出测试用例日志发生异常: %s." % e)
                            time.sleep(1)
                            continue
                    else:
                        if p_run_qttest.poll() == None:
                            time.sleep(1)
                            continue
                        elif p_run_qttest.poll() == 0:
                            logger.debug("Qt单体测试程序返回码: (%d)." % p_run_qttest.returncode)
                            return p_run_qttest.returncode
                        else:
                            logger.error("Qt单体测试程序返回码: (%d)." % p_run_qttest.returncode)
                            raise exceptions.RunOtherError("Qt单体测试程序%s运行错误。" % self._test_case_file.name)
                elif p_run_qttest.stderr in fd_set[0]:
                    errline = p_run_qttest.stderr.readline()
                    if errline:
                        sys.stdout.write(errline)
                        sys.stdout.flush()
                    if "Segmentation fault" in errline:
                        p_run_qttest.kill()
                        raise exceptions.SegmentationFault("Qt单体测试程序%s运行发生段错误。" % self._test_case_file.name)
                else:
                    p_run_qttest.kill()
                    raise exceptions.OutputTimeout("Qt单体测试程序单测试用例运行超时%d秒。" %  _caseoutput_timeout)
                _qttest_timeout = _qttest_timeout - (time.time() - while_begin)
                if _qttest_timeout <= 0:
                    p_run_qttest.kill()
                    raise exceptions.RuncaseTimeout("Qt单体测试程序总运行超时%d秒。" % _qttest_timeout)
            self._device.pull_file_from_device(os.path.join("tmp", test_result_file), \
                                               os.path.join(result_path, test_result_file))
        except OSError as e:
            logger.exception("运行Qt单体测试程序发生异常: %s." % e)
            raise
