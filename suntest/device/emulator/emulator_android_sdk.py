# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: emulator_android_sdk.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import re
import sys
import subprocess
import logging

from suntest.device.adb import ADB
from suntest.device.emulator.emulator import Emulator
from suntest.config import settings
from suntest.core import exceptions
import suntest.files.remove as Remove

logger = logging.getLogger(__name__)


class EmulatorAndroidSDK(Emulator):
    def __init__(self, **kwargs):
        super(EmulatorAndroidSDK, self).__init__(**kwargs)
        self.install_sdk = kwargs.get("install_sdk")
        self.emulator_args = kwargs.get("emulator_args", '')
        self._adb_path = os.path.join(self.install_sdk, "platform-tools/adb")
        self._emu_path = os.path.join(self.install_sdk, "emulator/emulator")

    def startup_device(self):
        """
        Description:
            startup the emulator with sdk package.
        Return: (bool)
        """
        startup_emulator_command = "%s %s" %(self._emu_path, self.emulator_args)
        logger.debug('启动模拟器命令: %s' % startup_emulator_command)
        if '-avd' not in startup_emulator_command:
            raise  exceptions.AvdNameNotSet("avd名字没有设置")
        super(EmulatorAndroidSDK, self).startup_device(startup_emulator_command, settings.emulator_process_name)
