# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: emulator_native_sdk.py
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


class EmulatorNativeSDK(Emulator):
    def __init__(self, **kwargs):
        super(EmulatorNativeSDK, self).__init__(**kwargs)
        self.install_sdk = kwargs.get("install_sdk")
        self.emulator_args = kwargs.get("emulator_args", "")
        self._adb_path = os.path.join(self.install_sdk, "platform-tools/adb")
        self._emu_path = os.path.join(self.install_sdk, "tools/nutshell-qemu")

    def startup_device(self):
        """
        Description:
            startup the emulator with sdk package.
        Return: (bool)
        """
        self.remove_var_image()

        startup_emulator_command = self._emu_path

        if self.emulator_args:
            startup_emulator_command = "%s %s" % (startup_emulator_command, self.emulator_args)
        if self.logcat:
            startup_emulator_command = "%s -logcat '%s'" % (startup_emulator_command, self.logcat)

        super(EmulatorNativeSDK, self).startup_device(startup_emulator_command, settings.emulator_process_name)

    def remove_var_image(self):
        """
        Description:
            remove all datas in var image.
        Return: (bool)
        """
        Remove.remove_spc_files(self.install_sdk, "var.img")
