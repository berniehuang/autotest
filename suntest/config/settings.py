# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: setting.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import logging
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
from functools import partial

logger = logging.getLogger(__name__)


class Settings(object):
    _opts = {'name': None,
             'workspace': None}

    def __init__(self):
        self._opts = self._opts.copy()
        self._custom_settings = dict()

    def __getitem__(self, key):
        return self._opts[key]

    def __setitem__(self, key, value):
        self._opts[key] = value

    @property
    def custom_settings(self):
        return self._custom_settings

    def load_cli_options(self, options):
        _options_dict = options.__dict__
        for key, default in self._opts.items():
            value = _options_dict[key] if key in _options_dict.keys() else default
            self[key] = value

    def load_config_file(self, config_file):
        try:
            config = ConfigParser()
            config.read(config_file)

            for option in config.options("unittest"):
                get_unittest = partial(config.get, "unittest")
                self._custom_settings[option] = get_unittest(option)
        except NoSectionError as e:
            logger.exception("项目配置文件%s中没有对应的section" % config_file)
            raise
        except Exception as e:
            logger.exception("解析项目配置文件发生异常。")
            raise


class SettingsUnitTest(Settings):
    _extra_opts = {'repo': None,
                   'type': None,
                   'gcov': False,
                   'gcov_filter': None,
                   'gcov_filter_section': None,
                   'exclude_unreachable_branches': None,
                   'exclude_throw_branches': None,
                   'lcov': False,
                   'jobs': None,
                   'jacoco': False,
                   'product': None,
                   'install_sdk': None,
                   'build_env': None,
                   'test_type': None,
                   'device_type': None,
                   'project_name': None,
                   'report_type': None,
                   'device_log': None,
                   'shell_args': None,
                   'logcat': None,
                   'emulator_args': None}

    def __init__(self):
        super(SettingsUnitTest, self).__init__()
        self._opts.update(self._extra_opts)

    def __str__(self):
        return """==============================================================================================================
     　　　　　　　　　　　　　                --基本设置--
工程名字: %(name)s
工程类型: %(type)s
结果目录: %(workspace)s
设备类型: %(device_type)s
报告类型: %(report_type)s
==============================================================================================================""" % dict(
            name = str(self.name),
            type = str(self.type),
            workspace = str(self.workspace),
            device_type = str(self.device_type),
            report_type = str(self.report_type))

    @property
    def name(self):
        return self['name']

    @property
    def workspace(self):
        return self['workspace']

    @property
    def type(self):
        return self['type']

    @property
    def report_type(self):
        return self['report_type']

    @property
    def product_type(self):
        return self['product']

    @property
    def test_type(self):
        return self._custom_settings.get('test_type')

    @property
    def project_name(self):
        return self._custom_settings.get('project_name')

    @property
    def device_type(self):
        return self['device_type'] or self._custom_settings.get('device_type')

    @property
    def compile_arch(self):
        return self._custom_settings.get('compile_arch')

    @property
    def encode(self):
        return self._custom_settings.get('encode', 'utf-8')

    @property
    def gcov_executable(self):
        return self._custom_settings.get('gcov_executable')

    @property
    def jacoco_reporter(self):
        return self._custom_settings.get('jack_jacoco_reporter')

    @property
    def android_version(self):
        return self._custom_settings.get('android_version')

    @property
    def toolchain(self):
        return self._custom_settings.get('toolchain')

    @property
    def tombstone_path(self):
        return self._custom_settings.get('tombstone_path')

    @property
    def emulator_process_name(self):
        return self._custom_settings.get('emulator_process_name')

    @property
    def simulator(self):
        return self._custom_settings.get('simulator')

    @property
    def compile_emu_env(self):
        return self._custom_settings.get('compile_emu_env')

    @property
    def compile_emu_cmd(self):
        return self._custom_settings.get('compile_emu_cmd')

    @property
    def install_sdk(self):
        return self._custom_settings.get('install_sdk')

    @property
    def device_config(self):
        return {'device_log': self._custom_settings.get('device_log'),
                'install_sdk': self['install_sdk'] or self._custom_settings.get('install_sdk'),
                'emulator_home': self._custom_settings.get('emulator_home'),
                'emulator_exec': self._custom_settings.get('emulator_exec'),
                'kernel_path': self._custom_settings.get('kernel_path'),
                'avd_name': self._custom_settings.get('avd_name'),
                'partition_size': self._custom_settings.get('partition_size'),
                'shell_args': self._custom_settings.get('shell_args'),
                'logcat': self['logcat'] or self._custom_settings.get('logcat'),
                'emulator_args': self._custom_settings.get('emulator_args'),
                'virtual_xserver': self._custom_settings.get('virtual_xserver')}


settings = SettingsUnitTest()
