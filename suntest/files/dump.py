# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: dump.py
# author: huangbin@pset.suntec.net
# date: 2020.6.2
# ------------------------------------------------------------------------------
import os
import logging
import subprocess

logger = logging.getLogger(__name__)


def dump_symbol_objfile(objfile, symbol='gcov'):
    """
    Description:
        dump all symbols from object file and find symbol.
    Return: (bool)
    Parameters:
        objfile: (str) dump objfile name.
        symbol: (str) find symbol name.
    """
    objdump_symbol_command = "objdump -s %s" % objfile
    try:
        p_objdump_symbol = subprocess.Popen(objdump_symbol_command, shell=True, stdout=subprocess.PIPE)
        while True:
            symbols_output = p_objdump_symbol.stdout.read()
            if symbols_output:
                if symbol in symbols_output:
                    logger.debug("中间文件%s已包含%s符号." % (objfile, symbol))
                    return True
                else:
                    logger.debug("中间文件%s不包含%s符号." % (objfile, symbol))
                    return False
            else:
                if p_objdump_symbol.poll() == None:
                    time.sleep(1)
                    continue
                elif p_objdump_symbol.poll() == 0:
                    break
                else:
                    break
    except OSError as e:
        logger.exception("导出中间文件符号表发生异常: %s" % e)
        raise

