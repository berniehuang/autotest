# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: compile_emu.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.11.25
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import sys
import time
import subprocess
import multiprocessing
import logging

from suntest.config import settings
from suntest.build.compile import Compile
import suntest.files.find as Find

logger = logging.getLogger(__name__)


class Compile_Emulator(Compile):
    def compile_emulator(self):
        """
        Description:
            make compile emulator.
        Return: (tool)
        """
        logging.info("开始编译模拟器...")
        compile_emu_cmd_list = settings.compile_emu_cmd.split(';')
        for compile_emu_cmd in compile_emu_cmd_list:
            return_code = self.make_compile(compile_emu_cmd, settings.compile_emu_env)
            if not return_code:
                logging.error("编译模拟器失败。")
                return return_code
            else:
                logging.info("编译模拟器成功。")

        if settings.device_type == "nativesdk":
            return_code = self.install_sdk()
            if return_code:
                return return_code
        return return_code

    def clean_emulator(self):
        """
        Description:
            make clean emulator.
        Return: (tool)
        """
        logging.info("开始清编译模拟器...")
        return_code = self.make_clean('')
        if not return_code:
            logging.error("清编译模拟器失败。")
        else:
            logging.info("清编译模拟器成功。")

        return return_code

    def install_sdk(self):
        """
        Description:
            install native sdk.
        Return: (tool)
        """
        if not os.path.exists(settings.install_sdk):
            os.makedirs(settings.install_sdk)

        install_sdk_shell_script = Find.find_file_path("out/host/linux-x86/native_sdk", "install.sh")
        install_sdk_args = [install_sdk_shell_script, "-t", settings.install_sdk]
        logger.debug("安装sdk命令: %s" % ' '.join(install_sdk_args))
        try:
            returncode = subprocess.check_call(install_sdk_args, stderr=subprocess.STDOUT)
            if returncode == 0:
                logger.info("安装sdk成功。")
                return True
            else:
                logger.error("安装sdk失败。")
                return False
        except Exception as e:
            logger.error("安装sdk发生异常: %s" % e)
            return False

