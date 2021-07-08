# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: device.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import sys
import time
import signal
import subprocess
from distutils.spawn import find_executable
import logging

from suntest.config import settings
from suntest.core import exceptions

logger = logging.getLogger(__name__)


class Device(object):
    """ android device
    """
    def __init__(self, **kwargs):
        self._adb_path = None

    @property
    def serial_number(self):
        """return the host connected device serial number"""
        return str(self.adb.get_serialno()).strip()

    @property
    def device_state(self):
        """return the host connected device state"""
        return str(self.adb.get_state()).strip()

    @property
    def devices_list(self):
        """return the host connected devices list"""
        return list(self.adb.get_devices())

    def check_binary_installed(self, name):
        """check the program whether or not installed"""
        self.adb.find_binary(name)
        if self.adb.get_output():
            logger.debug("which %s: %s" % (name, self.adb.get_output()))
            return True
        else:
            logger.error("which %s: %s" % (name, self.adb.get_error()))
            return False

    def check_path_exist(self, path):
        """
        Description:
            check path on device is or not exists.
        Return: (bool)
        Parameters:
            path (str) path on device
        """
        self.adb.set_adb_root()
        self.adb.shell_command(["ls", path])

        output = self.adb.get_output() or self.adb.get_error()
        if output:
            output = output.strip('\n').strip()
            if "No such file or directory" in output:
                logger.debug("设备上不存在文件或者目录%s" % path)
                return False
            else:
                return True
        else:
            logger.error("adb命令没有任何输出.")
            return False

    def get_property(self, key):
        """
        Description:
            get property on device.
        Return: (str) device property value
        Parameters:
            key (str) device property key
        """
        self.adb.set_adb_root()
        return_code = self.adb.get_return_code()
        if return_code == 0:
            logger.debug("获取adb的root权限成功。")
        else:
            logger.error("获取adb的root权限失败。[返回码] %s" % return_code)

        get_property_command = "getprop %s" % key
        logger.debug("获取设备%s属性命令: %s" % (key, get_property_command))

        get_property_args = [self._adb_path, "shell", get_property_command]
        try:
            p_get_property = subprocess.Popen(get_property_args, stdout=subprocess.PIPE)
            while True:
                property_value = p_get_property.stdout.read()
                logger.debug("设备属性%s的值: %s" % (key, property_value.strip()))
                if property_value:
                    return property_value
                else:
                    if p_get_property.poll() == None:
                        time.sleep(1)
                        continue
                    elif p_get_property.poll() == 0:
                        logger.debug("获取设备属性 [返回码] (%d)." % p_get_property.returncode)
                        break
                    else:
                        logger.debug("获取设备属性 [返回码] (%d)." % p_get_property.returncode)
                        break
        except OSError as e:
            logger.exception("get property exception %s." % e)
            raise

    def set_property(self, key, value, timeout=30):
        """
        Description:
            set property on device.
        Return: (bool)
        Parameters:
            key (str) device property key
            value (str) device property value
        """
        self.adb.set_adb_root()
        return_code = self.adb.get_return_code()
        if return_code == 0:
            logger.debug("获取adb的root权限成功。")
        else:
            logger.error("获取adb的root权限失败。[返回码] %s" % return_code)

        set_property_command = "setprop %s %s" % (key, value)
        logger.debug("设置设备%s属性命令: %s" % (key, set_property_command))

        set_property_args = [self._adb_path, "shell", set_property_command]
        try:
            p_set_property = subprocess.Popen(set_property_args, stdout=subprocess.PIPE)
            while True:
                return_code = p_set_property.poll()
                if return_code is None:
                    time.sleep(1)
                    timeout = timeout - 1
                else:
                    if return_code == 0:
                        logger.info("设置设备%s属性成功。" % key)
                        return True
                    else:
                        logger.error("设置设备%s属性失败。" % key)
                        return False
                if timeout == 0:
                    os.kill(p_set_property.pid, signal.SIGKILL)
                    logger.error("设置设备%s属性超时%d秒。" % (key ,timeout))
                    return False
        except OSError as e:
            logger.exception("设置设备属性异常: %s." % e)
            raise

    def push_file_to_device(self, local, remote):
        """
        Description:
            push host files to device by self.adb.
        Return: (bool)
        Parameters:
            local (str) local file path
            remote (str) remote path
        """
        self.adb.set_adb_root()
        return_code = self.adb.get_return_code()
        if return_code == 0:
            logger.debug("获取adb的root权限成功。")
        else:
            logger.error("获取adb的root权限失败。[返回码] %s" % return_code)

        self.adb.set_system_rw()
        return_code = self.adb.get_return_code()
        if return_code == 0:
            logger.debug("重新挂载system分区成功。")
        else:
            logger.error("重新挂载system分区失败。[返回码]: %s" % return_code)

        time.sleep(10)
        self.adb.push_local_file(local, remote)
        return_code = self.adb.get_return_code()
        if return_code == 0:
            return True
        else:
            logger.error("推送文件到设备上失败。[返回码]: %s" % return_code)
            return False

    def delete_path(self, path):
        """
        Description:
            delete path to device by self.adb.
        Return: (bool)
        Parameters:
            path (str) path to remove in device.
        """
        self.adb.set_adb_root()
        return_code = self.adb.get_return_code()
        if return_code == 0:
            logger.debug("获取adb的root权限成功。")
        else:
            logger.error("获取adb的root权限失败。[返回码] %s" % return_code)

        self.adb.remove_path(path)
        return_code = self.adb.get_return_code()
        if return_code == 0:
            logger.debug("删除文件%s成功" % path)
            return True
        else:
            logger.error("删除文件%s失败。[返回码]: %s" % return_code)
            return False

    def pull_file_from_device(self, remote, local):
        """
        Description:
            pull device files to host by self.adb.
        Return: (bool)
        Parameters:
            remote (str) remote file path
            local (str) local path
        """
        if settings.device_type != "anbox":
            self.adb.set_adb_root()
        return_code = self.adb.get_return_code()
        if return_code == 0:
            logger.debug("获取adb的root权限成功。")
        else:
            logger.error("获取adb的root权限失败。[返回码] %s" % return_code)

        self.adb.get_remote_file(remote, local)
        return_code = self.adb.get_return_code()
        if return_code == 0:
            return True
        else:
            logger.error("从设备上拉取文件%s到%s失败。[返回码]: %s" % (remote, local, return_code))
            return False

    def check_service_running(self, service_name):
        """
        Description:
            check service is or not running on device.
        Parameters:
            service_name: (str) need check service name.
        Return: (bool)
        """
        check_service_command = "service check %s" % service_name
        logger.debug("检查服务命令: %s" % check_service_command)

        check_service_args = [self._adb_path, "shell", check_service_command]
        try:
            p_check_service = subprocess.Popen(check_service_args, stdout=subprocess.PIPE)
            while True:
                check_service_result = p_check_service.stdout.read()
                logger.debug("检查服务结果: %s" % check_service_result.strip())
                if check_service_result:
                    try:
                        if check_service_result.strip() == "Service %s: found" % service_name:
                            return True
                        else:
                            return False
                    except IOError as e:
                        logger.exception("检查服务异常: %s." % e)
                        time.sleep(1)
                        continue
                else:
                    if p_check_service.poll() == None:
                        time.sleep(1)
                        continue
                    elif p_check_service.poll() == 0:
                        logger.debug("检查服务 [返回码]: (%d)." % p_check_service.returncode)
                        break
                    else:
                        logger.debug("检查服务 [返回码]: (%d)." % p_check_service.returncode)
                        break
        except OSError as e:
            logger.exception("检查服务异常: %s." % e)
            raise

    def check_service_list(self, service_list, timeout=60):
        """
        Description:
            check all services
        Return: (bool)
        Parameters:
            service_list (list) check service list
            timeout (int) timeout for check service
        """
        while_begin = time.time()
        while service_list:
            for service in service_list:
                if self.check_service_running(service):
                    service_list.remove(service)

            time.sleep(3)
            timeout = timeout - (time.time() - while_begin)
            if timeout <= 0:
                logger.error("在设备上没有发现服务%s." % ' '.join(service_list))
                return False

            continue

        return True

    def install_package(self, package):
        """
        Description:
            install package on device by adb
        Return: (bool)
        Parameters:
            package (str) package name
        """
        self.check_service_list(["package", "mount"])
        self.adb.install(pkgapp=package, reinstall=True)
        return_code = self.adb.get_return_code()
        if return_code == 0:
            return True
        else:
            logger.error("在设备上安装包%s失败。 [返回码]: %s [错误信息]: %s" % (package, return_code, self.adb.get_error()))
            return False

    def uninstall_package(self, package):
        """
        Description:
            uninstall package on device by adb
        Return: (bool)
        Parameters:
            package (str) package name
        """
        self.adb.uninstall(package)
        return_code = self.adb.get_return_code()
        if return_code == 0:
            return True
        else:
            logger.warning("在设备上卸载包%s失败。 [返回码]: %s [错误信息]: %s" % (package, return_code, self.adb.get_error()))
            return False

    def get_pid(self, program, timeout=30):
        """
        Description:
            get the host connected devices program id
        Returns: (list) program id.
        Parameters:
            program: the target program name.
        """
        pid = None

        if not isinstance(program, basestring):
            raise TypeError("program must be a string.")

        if not program:
            logger.error("program name %s is empty.")
            return pid

        get_pid_command = "ps | grep %s" % program
        get_pid_args = [self._adb_path, "shell", get_pid_command]
        try:
            p_get_pid = subprocess.Popen(get_pid_args, stdout=subprocess.PIPE)
            while True:
                return_code = p_get_pid.poll()
                if return_code is None:
                    time.sleep(1)
                    timeout = timeout - 1
                else:
                    if return_code == 0:
                        process_info = p_get_pid.stdout.read().strip().split()
                        if process_info:
                            pid = process_info[1]
                            logger.debug("get pid: %s" % pid)
                            return pid
                        else:
                            logger.error("%s process info is null." % get_pid_command)
                            break
                    else:
                        logger.error("%s Failed!" % get_pid_command)
                        return False
                if timeout == 0:
                    os.kill(p_get_pid.pid, signal.SIGKILL)
                    logger.error("%s TIMEOUT %d seconds." % (get_pid_command ,timeout))
                    return False
        except Exception as e:
            logger.exception("get pid execption %s." % e)
            raise

    def crashreporter(self, pid=0, timeout=30):
        """
        Description:
            trigger a program crash report.
        Returns: (list) program id.
        Parameters:
            pid: the target program id.
        """
        crashreporter_command = "crashreporter %s" % str(pid)
        crashreporter_args = [self._adb_path, "shell", crashreporter_command]
        try:
            p_crashreporter = subprocess.Popen(crashreporter_args, stdout=subprocess.PIPE)
            while True:
                return_code = p_crashreporter.poll()
                if return_code == 0:
                    content = p_crashreporter.stdout.read()
                    logger.debug("crashreport content: %s" % str(content))
                    crashdump_filepath = content[content.find("/var/system/grave"):].strip()
                    if crashdump_filepath:
                        self.adb.get_remote_file(settings.tombstone_path, crashdump_filepath)
                    return crashdump_filepath
                else:
                    time.sleep(1)
                    timeout = timeout - 1
                if timeout == 0:
                    p_crashreporter.kill()
                    logger.error("%s TIMEOUT %d seconds." % (crashreporter_command ,timeout))
                    return False
        except Exception as e:
            logger.exception("trigger crashreport exception %s." % e)
            raise

    def get_process_list(self, timeout=30):
        """
        Description:
            get process list on device.
        Returns: (list) process list.
        """
        process_list = list()

        process_list_args = [self._adb_path, "shell", "ps"]
        try:
            p_process_list = subprocess.Popen(process_list_args, stdout=subprocess.PIPE)
            while True:
                return_code = p_process_list.poll()
                if return_code == 0:
                    content = p_process_list.stdout.read().strip().split('\n')
                    process_list = [process_info.split()[8] for process_info in content[1:]]
                    return process_list
                else:
                    time.sleep(1)
                    timeout = timeout - 1
                if timeout == 0:
                    p_process_list.kill()
                    logger.error("获取设备进程列表超时%d秒." % timeout)
                    return False
        except Exception as e:
            logger.exception("获取设备进程列表超发生异常%s." % e)
            raise

    def startup_device(self):
        """
        Description:
            startup the specify device
        Return: (bool)
        """
        raise NotImplementedError

    def stop_device(self):
        """
        Description:
            stop the specify device
        Return: (bool)
        """
        raise NotImplementedError
