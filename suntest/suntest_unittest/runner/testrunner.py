# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: testrunner.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import time
import logging

import suntest.files.dump as Dump
from suntest import ExitStatus
from suntest.core import exceptions
from suntest.config import settings
from suntest.suntest_unittest.coverage.gcov import Gcov

logger = logging.getLogger(__name__)


class TestFile(object):
    def __init__(self, test_file_config):
        self.name = test_file_config.get("name", "")
        self.local = test_file_config.get("local", "")
        self.remote = test_file_config.get("remote", "")


class TestCaseFile(TestFile):
    def __init__(self, test_case_file_config):
        super(TestCaseFile, self).__init__(test_case_file_config)


class TestLibraryFile(TestFile):
    def __init__(self, test_library_file_config):
        super(TestLibraryFile, self).__init__(test_library_file_config)
        self._gcno_generate_path = test_library_file_config.get("gcno_generate_path", "")
        # feature for replace absolute path with PWD in gcno generate path
        self._gcno_generate_path = self._gcno_generate_path.strip(os.path.sep).replace("$PWD", "%s" % os.environ.get("PWD"))

        self._head_generate_path = test_library_file_config.get("head_generate_path", "")
        # feature for replace absolute path with PWD in head generate path
        self._head_generate_path = self._head_generate_path.strip(os.path.sep).replace("$PWD", "%s" % os.environ.get("PWD"))

        self._application_path = test_library_file_config.get("application_path", "")


class ResourceFile(TestFile):
    def __init__(self, resource_file_config):
        super(ResourceFile, self).__init__(resource_file_config)


class TestRunner(object):
    def __init__(self, test_config, device):
        self.test_result_flag = ExitStatus.OK
        self._type = str(test_config.get("type", ""))
        self._product_type = str(test_config.get("product_type", ""))
        self._project_name = str(test_config.get("project_name", ""))
        self._test_case_file = TestCaseFile(test_config.get("test_case_file", {}))
        self._test_library_files = [TestLibraryFile(test_library_config) for test_library_config in test_config.get("test_library_files", [])]
        self._resource_files = [ResourceFile(resource_file_config) for resource_file_config in test_config.get("resource_files", [])]
        self._source_code_path = str(test_config.get("source_code_path", ""))
        self._set_env = str(test_config.get("set_env", ""))
        self._get_prop = list(test_config.get("get_prop", []))
        self._set_prop = list(test_config.get("set_prop", []))
        self._result_report = str(test_config.get("result_report", "test-result-%s.xml" % (self._test_case_file)))
        self._start_service_list = list(test_config.get("start_service_list", []))
        self._kill_service_list = list(test_config.get("kill_service_list", []))
        self._gcda_generate_path = str(test_config.get("gcda_generate_path", ""))
        self._gcov_exclude = list(test_config.get("gcov_exclude", []))
        self._gcov_filter = list(test_config.get("gcov_filter", []))
        self._lcov_exclude = list(test_config.get("lcov_exclude", []))
        self._lcov_filter = list(test_config.get("lcov_filter", []))
        self._package_filter = list(test_config.get("package_filter", []))
        self._class_filter = list(test_config.get("class_filter", []))
        self._device = device

    def __str__(self):
        return """[测试框架类型]: %(type)s
[测试程序名]: %(test_case_file)s
[被测程序名]: %(test_library_files)s
[资源文件名]: %(resource_files)s
[源代码路径]: %(source_code_path)s""" % dict(
            type = str(self._type),
            test_case_file = str(self._test_case_file.name),
            test_library_files = str(' '.join([test_library_file.name for test_library_file in self._test_library_files])),
            resource_files = str(' '.join([resource_file.name for resource_file in self._resource_files])),
            source_code_path = str(self._source_code_path))

    @property
    def type(self):
        return self._type

    @property
    def device(self):
        return self._device

    @property
    def test_case_file(self):
        return self._test_case_file

    @property
    def source_code_path(self):
        return self._source_code_path

    @property
    def test_library_files(self):
        return self._test_library_files

    @property
    def product_type(self):
        return self._product_type

    @property
    def project_name(self):
        return self._project_name

    @property
    def result_report(self):
        return self._result_report

    @property
    def gcda_generate_path(self):
        return self._gcda_generate_path

    @property
    def gcov_exclude(self):
        return self._gcov_exclude

    @property
    def gcov_filter(self):
        return self._gcov_filter

    @property
    def lcov_exclude(self):
        return self._lcov_exclude

    @property
    def lcov_filter(self):
        return self._lcov_filter

    @property
    def package_filter(self):
        return self._package_filter

    @property
    def class_filter(self):
        return self._class_filter

    @property
    def test_name(self):
        return self._test_case_file.name

    def run(self, workspace):
        """
        Description:
            run the unittest program.
        Parameters:
            workspace: (str) test result store path.
        Return: (tool)
        """
        try:
            self.start_device()
        except exceptions.DeviceStartupFailure as e:
            self.test_result_flag = ExitStatus.DEVICE_STARTUP_FAILED
            return self.test_result_flag
        try:
            self.set_property_on_device()
            self.get_property_on_device()
            self.push_files_to_device()
            self.execute_testcase(self.result_report)
            self.pull_result_from_device(self.result_report, workspace)
            if settings['gcov']:
                self.assemble_coverage_files()
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
        finally:
            self.stop_device()
            time.sleep(10)
            return self.test_result_flag

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

    def get_property_on_device(self):
        """
        Description:
           set property on device.
        """
        for get_prop in self._get_prop:
            key = get_prop.get("key", "")
            self._device.get_property(key)

    def set_property_on_device(self):
        """
        Description:
            set property on device.
        """
        for set_prop in self._set_prop:
            key = set_prop.get("key", "")
            value = set_prop.get("value", "")
            if type(value) == bool:
                value = str(value).lower()
            self._device.set_property(key, value)

    def push_files_to_device(self):
        """
        Description:
            push test case file and test library files and resource files to device.
        Return: (tool)
        """
        push_list = list()

        push_list.append(self._test_case_file)
        push_list.extend(self._test_library_files)
        push_list.extend(self._resource_files)

        for push_file in push_list:
            local_push_file = os.path.join(push_file.local, push_file.name)
            remote_push_file = os.path.join(push_file.remote, push_file.name)
            if self._device.check_path_exist(remote_push_file):
                logger.debug("%s已经存在设备中。" % remote_push_file)
                continue
            Dump.dump_symbol_objfile(local_push_file)
            if self._device.push_file_to_device(local_push_file, remote_push_file):
                logger.debug("推送文件%s到设备的%s目录成功。" % (local_push_file, remote_push_file))
            else:
                logger.error("推送文件%s到设备的%s目录失败。" % (local_push_file, remote_push_file))
                raise exceptions.PushFileFailure("推送文件到设备时发生异常。")

    def install_package_to_device(self, package):
        """
        Description:
            install package on device
        Parameters:
            package: (str) package name.
        Return: (tool)
        """
        if self._device.install_package(package):
            logger.debug("在设备上安装%s成功。" % package)
        else:
            raise exceptions.InstallPackageFailure("在设备上安装%s失败。" % package)

    def uninstall_package_to_device(self, package):
        """
        Description:
            uninstall package on device
        Parameters:
            package: (str) package name.
        Return: (tool)
        """
        if self._device.uninstall_package(package):
            logger.debug("在设备上卸载%s成功。" % package)
        else:
            logger.warning("在设备上卸载%s失败。" % package)

    def execute_testcase(self, result_report):
        """
        execute test program
        interface implemented by concrete impls
        """
        raise NotImplementedError

    def pull_result_from_device(self, result_report, workspace):
        """
        Description:
            pull result report from device to local.
        Parameters:
            result_report: (str) test result report file.
            workspace: (str) project workspace.
        Return: (tool)
        """
        logger.debug("从设备上拉取单体测试结果报告%s." % (result_report))
        self._device.pull_file_from_device(os.path.join("data", result_report), \
                                           os.path.join(workspace, result_report))

    def assemble_coverage_files(self):
        """
        Description:
            assemble all type coverage files for all test library files to source code path.
        Parameters:
        """
        for test_library_file in self.test_library_files:
            gcov_object = Gcov(self.source_code_path, test_library_file._gcno_generate_path, \
                               self.gcda_generate_path, test_library_file._head_generate_path)
            gcov_object.assemble_gcov_files(self.device)
