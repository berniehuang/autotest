# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: gtestrunner.py
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

logger = logging.getLogger(__name__)


class GtestRunner(TestRunner):
    def execute_testcase(self, result_report, gtest_filter=None):
        """
        Description:
            execute google test program on device.
        Return: (bool)
        Parameters:
            result_report: (str) the googletest result report.
            gtest_filter: (str) googletest case filter pattern.
        """
        _googletest_timeout = 3600
        _caseoutput_timeout = 300

        if not gtest_filter:
            run_googletest_command = "%s %s --gtest_output=xml:%s" \
            % (self._set_env, self._test_case_file.name, os.path.join("data", result_report))
        else:
            run_googletest_command = "%s %s --gtest_filter=*%s* --gtest_output=xml:%s" \
            % (self._set_env, self._test_case_file.name, gtest_filter, os.path.join("data", result_report))

        logger.debug("运行googletest单体测试程序的命令: %s" % run_googletest_command)

        logger.info("开始运行googletest测试用例...")
        run_googletest_args = [self._device._adb_path, "-s", self._device.serial_number, "shell", run_googletest_command]
        try:
            p_run_googletest = subprocess.Popen(run_googletest_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                while_begin = time.time()
                fd_set = select.select([p_run_googletest.stdout, p_run_googletest.stderr], [], [], _caseoutput_timeout)
                if p_run_googletest.stdout in fd_set[0]:
                    logline = p_run_googletest.stdout.readline()
                    if logline:
                        try:
                            sys.stdout.write(logline)
                            sys.stdout.flush()
                        except IOError as e:
                            logger.exception("输出测试用例日志发生异常: %s." % e)
                            time.sleep(1)
                            continue
                    else:
                        if p_run_googletest.poll() == None:
                            time.sleep(1)
                            continue
                        elif p_run_googletest.poll() == 0:
                            logger.debug("googletest单体测试程序返回码: (%d)." % p_run_googletest.returncode)
                            return p_run_googletest.returncode
                        else:
                            logger.error("googletest单体测试程序返回码: (%d)." % p_run_googletest.returncode)
                            raise exceptions.RunOtherError("googletest单体测试程序%s运行错误。" % self._test_case_file.name)
                elif p_run_googletest.stderr in fd_set[0]:
                    errline = p_run_googletest.stderr.readline()
                    if errline:
                        sys.stdout.write(errline)
                        sys.stdout.flush()
                    if "Segmentation fault" in errline:
                        p_run_googletest.kill()
                        raise exceptions.SegmentationFault("googletest单体测试程序%s运行发生段错误。" % self._test_case_file.name)
                else:
                    p_run_googletest.kill()
                    raise exceptions.OutputTimeout("googletest单体测试程序单测试用例运行超时%d秒。" % _caseoutput_timeout)
                _googletest_timeout = _googletest_timeout - (time.time() - while_begin)
                if _googletest_timeout <= 0:
                    p_run_googletest.kill()
                    raise exceptions.RuncaseTimeout("googletest单体测试程序总运行超时%d秒。" % _googletest_timeout)
        except OSError as e:
            logger.exception("运行googletest单体测试程序发生异常: %s." % e)
            raise
