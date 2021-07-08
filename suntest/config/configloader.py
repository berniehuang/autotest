# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: configloader.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.3.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import sys
import yaml
import logging
from logging.config import dictConfig
from logging.config import fileConfig

from suntest.core import exceptions
from suntest.config import settings
from suntest.config import CONFIG_PATH


class ConfigLoader(object):
    def __init__(self, options):
        self.options = options

    def load_logging_config(self):
        """
        Description:
            load logging config file
        Return: (bool)
        """
        try:
            log_config_file = os.path.join(CONFIG_PATH, "logging.yaml")
            if os.path.exists(log_config_file):
                with open(log_config_file, 'r') as f:
                    log = yaml.safe_load(f)

                # set loglevel by command args
                log['root']['level'] = self.options.loglevel

                dictConfig(log)
            else:
                fileConfig(os.path.join(config_path, "logging.conf"))
        except IOError as e:
            logging.exception("导入日志配置文件发生异常: %s." % e)
            raise
        except ValueError:
            logging.exception("日志等级是未可知的。")
            raise

    def load_project_config(self):
        """
        Description:
            load project config file
        Return: (bool)
        """
        settings.load_cli_options(self.options)
        project_config_file = self.options.settings if self.options.settings else os.path.join(CONFIG_PATH, "%s.conf" % self.options.project)
        if not os.path.exists(project_config_file):
            raise exceptions.ProjectConfigNoExist("项目配置文件%s不存在。" % project_config_file)
        settings.load_config_file(project_config_file)
        print settings
