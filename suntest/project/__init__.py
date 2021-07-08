# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Module:   project
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import re
import sys
import logging

from suntest.config import settings
from suntest.util.manifests import Manifests
from suntest.project.project_unittest import ProjectUnitTest
from suntest.project.project_smoketest import ProjectSmokeTest
from suntest.device import DeviceFactory
import suntest.files.remove as Remove

logger = logging.getLogger(__name__)


class ProjectFactory(object):
    operator = {'unittest': ProjectUnitTest, 'smoketest': ProjectSmokeTest}

    @staticmethod
    def get_project_object(type, name, workspace, config, tasks):
        if not os.path.exists(settings['workspace']):
            os.mkdir(settings['workspace'])
        else:
            if ProjectUnitTest.build_tasks == tasks or ['build'] == tasks:
                os.path.walk(settings['workspace'], Remove.remove_files_excl_file, ("autotest.log"))

        device = DeviceFactory.get_device_object(settings.device_type, **settings.device_config)
        return ProjectFactory.operator.get(type, 'unittest')(name, workspace, device, config, tasks)
