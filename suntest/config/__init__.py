# -*- coding: UTF-8 -*-
import os

CONFIG_PATH = __file__.split('__init__.py')[0]
PROJECTS = '\n'.join([os.path.splitext(filename)[0] for filename in os.listdir(CONFIG_PATH) if filename.endswith(".conf")])
__all__ = ['settings']

from settings import settings
