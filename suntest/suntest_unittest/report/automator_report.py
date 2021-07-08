# -*- coding: UTF-8 -*-


import os
import logging

from suntest.tools import TOOLS_PATH
import suntest.core.command as Command

logger = logging.getLogger(__name__)

class Automator2JunitXml(object):
    """automator-log-converter"""
    tool_path = os.path.join(TOOLS_PATH, 'automator-log-converter-1.5.0.jar')

    @staticmethod
    def converter(log_file):
        """
        Read Android UI automator file output and write a JUNIT xml to same dir.

        log_file: file with output from automator.
        """

        if not os.path.exists(log_file):
            logger.error('测试程序结果log文件 %s不存在' % log_file)
            return
        automator_log_coverter_cmd = 'java -jar %s %s' % (Automator2JunitXml.tool_path, log_file)
        logger.debug('测试程序结果log文件转为xml文件命令: %s ' % automator_log_coverter_cmd)
        if not Command.shell_command(automator_log_coverter_cmd):
            logger.error("测试程序结果log文件转为xml文件失败")
        else:
            logger.info('测试程序结果log文件转为xml文件成功')