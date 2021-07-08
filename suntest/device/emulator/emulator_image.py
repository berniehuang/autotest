# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: emulator_runemu.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.9.12
# ------------------------------------------------------------------------------
import os
import stat
import subprocess
import logging

from suntest.config import settings
from suntest.device.emulator.emulator import Emulator

logger = logging.getLogger(__name__)


class EmulatorImage(Emulator):
    """the emulator from make compile complete."""
    def __init__(self, **kwargs):
        super(EmulatorImage, self).__init__(**kwargs)
        self.emulator_args = kwargs.get("emulator_args", '')
        self.kernel_path = kwargs.get("kernel_path")
        self._adb_path = os.path.join(os.environ['%s_HOST_OUT' % settings.compile_arch], "bin/adb")
        self._emu_path = kwargs.get("emulator_exec")

    def startup_device(self):
        system_path = os.path.join(os.environ.get("%s_PRODUCT_OUT" % settings.compile_arch), "system.img")
        ramdisk_path = os.path.join(os.environ.get("%s_PRODUCT_OUT" % settings.compile_arch), "ramdisk.img")
        userdata_path = os.path.join(os.environ.get("%s_PRODUCT_OUT" % settings.compile_arch), "userdata.img")
        for path in [self.kernel_path, system_path, ramdisk_path, userdata_path]:
            if not os.path.exists(path):
                logger.error("模拟器启动设置路径%s不存在。" % path)
                return False

        #startup_emulator_command = "%s -kernel %s -system %s -ramdisk %s -data %s -nocache -show-kernel" \
        #% (self._emu_path, self.kernel_path, system_path, ramdisk_path, userdata_path)
        startup_emulator_command = "%s -kernel %s -system %s -ramdisk %s -nocache -show-kernel" \
        % (self._emu_path, self.kernel_path, system_path, ramdisk_path)

        startup_emulator_command = "%s %s" %(startup_emulator_command, self.emulator_args)
        if self.emulator_home:
            startup_emulator_command = "PREBUILTS_HOME=%s %s" % (os.path.join(os.getcwd(), self.emulator_home), startup_emulator_command)

        super(EmulatorImage, self).startup_device(startup_emulator_command, settings.emulator_process_name)
