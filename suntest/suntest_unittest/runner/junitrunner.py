# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: junitrunner.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.3.12
# ------------------------------------------------------------------------------
import os
import re
import sys
import time
import select
import subprocess
import logging

import suntest.files.copy as Copy
from testrunner import TestRunner
from suntest import ExitStatus
from suntest.core import exceptions
from suntest.config import settings
from suntest.suntest_unittest.report.automator_report import Automator2JunitXml
logger = logging.getLogger(__name__)


class CodePackage(object):
    def __init__(self, package_config):
        self.name = package_config.get("name", "")
        self.package_name = package_config.get("package_name", "")
        self.local = package_config.get("local", "")

class TestPackage(object):
    def __init__(self, test_package_config):
        self.name = test_package_config.get("name", "")
        self.package_name = test_package_config.get("package_name", "")
        self.local = test_package_config.get("local", "")
        self.classfiles_path = test_package_config.get("classfiles_path", "")
        self.coverage_em_path = test_package_config.get("coverage_em_path", "")
        self.javanote_file = str()

    def get_javanote_filepath(self, android_version):
        mapping = {
                'Android8': self.get_coverage_emfile,
                'Android9': self.get_classfile
        }
        self.javanote_file = mapping[android_version]()
        return self.javanote_file

    def get_javanote_filename(self, android_version):
        return os.path.basename(self.get_javanote_filepath(android_version))

    def get_classfile(self):
        classfile = None
        try:
            for filename in os.listdir(self.classfiles_path):
                if re.match(r".*classes.jar", filename):
                    classfile = filename
        except Exception as e:
            logger.exception("匹配classfile错误。")
        finally:
            return os.path.join(self.classfiles_path, classfile)

    def get_coverage_emfile(self):
        coverage_emfile = os.path.join(self.coverage_em_path, 'coverage.em')
        if not os.path.exists(coverage_emfile):
            logger.exception("coverage.em文件不存在")
            return None
        else:
            return coverage_emfile

class JUnitRunner(TestRunner):
    def __init__(self, test_config, device):
        super(JUnitRunner, self).__init__(test_config, device)
        self._test_package = TestPackage(test_config.get("test_package", {}))
        self._source_code_path = test_config.get("source_code_path", "")
        self._code_packages = [CodePackage(code_package_config) for code_package_config in test_config.get("code_packages", [])]
        #The coverage.ec file will be generated in different paths depending on CE or DE
        self.coverage_ec_exist_file = str()
        self.coverage_ec_files = [
            os.path.join("/data", d, "0" ,self.test_package.package_name, "files/coverage.ec")
            for d in ('user', 'user_de')]

    def __str__(self):
        return """[测试框架类型]: %(type)s
[测试安装包]: %(test_package)s
[源码安装包]: %(code_packages)s""" % dict(
            type = str(self._type),
            test_package = str(self._test_package.name),
            code_packages = str(' '.join([code_package.name for code_package in self._code_packages])))

    @property
    def test_package(self):
        return self._test_package

    @property
    def code_packages(self):
        return self._code_packages

    @property
    def coverage_ec(self):
        return os.path.splitext(self.result_report)[0] + '.ec'

    @property
    def test_name(self):
        return self._test_package.name

    def get_javanote_filename(self):
        return self.test_package.get_javanote_filename(settings.android_version)

    def assemble_coverage_files(self, workspace):
        """
        Description:
            assemble java unittest java note files and coverage ec files.
        Parameters:
            workspace: (str) project workspace.
        Return: (tool)
        """
        logger.debug("拷贝%s到%s。" % (self.test_package.get_javanote_filepath(settings.android_version), workspace))
        dir_name, base_name =  os.path.split(self.test_package.javanote_file)
        Copy.copy_file(dir_name, workspace, base_name)

        logger.debug("从设备上拉取coverage.ec文件。")
        self.coverage_ec_exist_file = ' '.join(filter(self.device.check_path_exist, self.coverage_ec_files))
        if not self.coverage_ec_exist_file:
            logger.error("设备上没有coverage.ec文件")
        else:
            self.device.pull_file_from_device(self.coverage_ec_exist_file, os.path.join(workspace, self.coverage_ec))

    def run(self, workspace):
        """
        Description:
            run the unittest program.
        Parameters:
            workspace: (str) test result store path.
        Return: (tool)
        """
        result_log = os.path.join(workspace, os.path.splitext(self.result_report)[0] + '.log')

        try:
            self.start_device()
        except exceptions.DeviceStartupFailure as e:
            self.test_result_flag = ExitStatus.DEVICE_STARTUP_FAILED
            return self.test_result_flag
        try:
            self.set_property_on_device()
            self.get_property_on_device()
            self.install_packages()
            self.execute_testcase(result_log)
            Automator2JunitXml.converter(result_log)
            if settings['jacoco']:
                self.assemble_coverage_files(workspace)
        except exceptions.PushFileFailure:
            self.test_result_flag = ExitStatus.PUSH_FAILURE
        except exceptions.SegmentationFault as e:
            e.exceptionhandler(self._device, self.test_case_file.name)
            self.test_result_flag = ExitStatus.SEGMENT_FAULT
        except exceptions.OutputTimeout as e:
            e.exceptionhandler(self._device, self.test_case_file.name)
            self.test_result_flag = ExitStatus.OUTPUT_TIMEOUT
        except exceptions.RuncaseTimeout as e:
            e.exceptionhandler(self._device, self.test_case_file.name)
            self.test_result_flag = ExitStatus.RUN_TIMEOUT
        except exceptions.RunOtherError as e:
            e.exceptionhandler(self._device, self.test_case_file.name)
            self.test_result_flag = ExitStatus.OTHER_RUN_ERROR
        except exceptions.InstallPackageFailure as e:
            self.test_result_flag = ExitStatus.INSTALL_FAILURE
        finally:
            self.stop_device()
            time.sleep(10)
            return self.test_result_flag

    def get_package_name(self):
        """
        Description:
            get junit package name on device.
        Return: (list) packages
        """
        _package_names = [code_package.package_name for code_package in self.code_packages]
        _package_names.append(self.test_package.package_name)

        return _package_names

    def get_package_path(self):
        """
        Description:
            get junit package path on device.
        Return: (list) packages
        """
        _package_paths = [os.path.join(code_package.local, code_package.name) for code_package in self.code_packages if os.path.exists(code_package.local)]
        _package_paths.append(os.path.join(self.test_package.local, self.test_package.name))

        return _package_paths

    def install_packages(self):
        install_packages = self.get_package_path()
        for install_package in install_packages:
            self.install_package_to_device(install_package)

    def uninstall_packages(self):
        uninstall_packages = self.get_package_name()
        for uninstall_package in uninstall_packages:
            self.uninstall_package_to_device(uninstall_package)

    def get_installed_package_instrumentation(self):
        """
        Description:
            get package instrumentation on device.
        Return: (dict) instrumentation dict
        """
        _package_instrumentation_dict = dict()

        list_instrumentation_command = "pm list instrumentation"
        logger.debug("列出所有的instrumentation测试包。")

        list_instrumentation_args = [self._device._adb_path, "-s", self._device.serial_number, "shell", list_instrumentation_command]
        try:
            p_list_instrumentation = subprocess.Popen(list_instrumentation_args, stdout=subprocess.PIPE)
            instrumentation_lines = p_list_instrumentation.stdout.readlines()
            for instrumentation_line in instrumentation_lines:
                instrumentation = instrumentation_line.strip('\n')
                key = instrumentation[(instrumentation.find('target=') + len('target=')):instrumentation.find(')')]
                value = instrumentation[(instrumentation.find('instrumentation:') + len('instrumentation:')):instrumentation.find(' ')]
                _package_instrumentation_dict[key] = value
        except OSError as e:
            logger.exception("列出所有的instrumentation测试包发生异常: %s." % e)
            raise

        return _package_instrumentation_dict

    def execute_testcase(self, result_log):
        """
        Description:
            execute junit test program on device.
        Return: (bool)
        """
        _junit_timeout = 3600
        _caseoutput_timeout = 300
        _extra_options = str()

        package_instrumentation_dict = self.get_installed_package_instrumentation()
        if package_instrumentation_dict.has_key(self.test_package.package_name):
            logger.debug("%s已经被安装到设备上。" % self.test_package.package_name)
        else:
            logger.error("%s还没有被安装到设备上。" % self.test_package.package_name)
            return False

        if settings['jacoco']:
            _extra_options = '-e coverage true'
        if self.package_filter:
            _package_filter_options = ' '.join(package_filter for package_filter in self.package_filter)
            _extra_options = "%s -e package %s" % (_extra_options, _package_filter_options)
        if self.class_filter:
            _class_filter_options = ','.join(class_filter for class_filter in self.class_filter)
            _extra_options = "%s -e class %s" % (_extra_options, _class_filter_options)

        run_junit_command = "am instrument -r -w %s %s" \
            % (_extra_options, package_instrumentation_dict.get(self.test_package.package_name))
        logger.debug("java单体测试的运行命令: %s" % run_junit_command)
        _check_service_timeout = 30
        while True:
            while_begin = time.time()
            if self._device.check_service_running("activity"):
                break
            else:
                time.sleep(3)
                _check_service_timeout = _check_service_timeout - (time.time() - while_begin)
                if _check_service_timeout <= 0:
                    logger.error("设备上没有发现activity manager。")
                    return False
                continue
        # (temp revise) waiting for activity manager launched completely
        time.sleep(20)

        logger.info("开始运行junit测试用例...")
        run_junit_args = [self._device._adb_path, "-s", self._device.serial_number, "shell", run_junit_command]
        try:
            p_run_junit = subprocess.Popen(run_junit_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                while_begin = time.time()
                fd_set = select.select([p_run_junit.stdout, p_run_junit.stderr], [], [], _caseoutput_timeout)
                if p_run_junit.stdout in fd_set[0]:
                    logline = p_run_junit.stdout.readline()
                    if logline:
                        try:
                            sys.stdout.write(logline)
                            sys.stdout.flush()
                        except IOError as e:
                            logger.exception("输出测试用例日志发生异常: %s." % e)
                            time.sleep(1)
                            continue
                        try:
                            with open(result_log, 'a') as f:
                                f.write(logline)
                        except IOError as e:
                            logger.exception("打开单体测试结果文件发生异常 %s." % e)
                            break
                    else:
                        if p_run_junit.poll() == None:
                            time.sleep(1)
                            continue
                        elif p_run_junit.poll() == 0:
                            logger.debug("java单体测试程序的返回码 (%d)." % p_run_junit.returncode)
                            return p_run_junit.returncode
                        else:
                            logger.error("java单体测试程序的返回码 (%d)." % p_run_junit.returncode)
                            raise exceptions.RunOtherError("java单体测试程序%s运行错误。" % self._test_package.name)
                elif p_run_junit.stderr in fd_set[0]:
                    errline = p_run_junit.stderr.readline()
                    if errline:
                        sys.stdout.write(errline)
                        sys.stdout.flush()
                    if "Segmentation fault" in errline:
                        p_run_junit.kill()
                        raise exceptions.SegmentationFault("java单体测试程序%s运行发生段错误。" % self._test_package.name)
                else:
                    p_run_junit.kill()
                    raise exceptions.OutputTimeout("java单体测试程序单测试用例运行超时%d秒。" % _caseoutput_timeout)
                _junit_timeout = _junit_timeout - (time.time() - while_begin)
                if _junit_timeout <= 0:
                    p_run_junit.kill()
                    raise exceptions.RuncaseTimeout("java单体测试程序总运行超时%d秒。" % _junit_timeout)
        except OSError as e:
            logger.exception("运行java单体测试程序发生异常 %s." % e)
            raise
