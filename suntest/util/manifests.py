# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: manifests.py
# Author:   huangbin@pset.suntec.net
# Date:     2017.3.6
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import logging
import xml.dom.minidom as minidom

logger = logging.getLogger(__name__)


class Manifests(object):
    def __init__(self):
        self.project_list = list()
        self.remote_list = list()
        self.remote_dict = dict()

    def get_remote_list(self, manifest_xml):
        try:
            dom = minidom.parse(manifest_xml)
            root = dom.documentElement

            remote_list = root.getElementsByTagName("remote")
            self.remote_list.extend(remote_list)

            include_list = root.getElementsByTagName("include")
            for include in include_list:
                include_manifest_xml = include.getAttribute("name")
                self.get_remote_list(os.path.join(os.path.dirname(manifest_xml), include_manifest_xml))
        except IOError as e:
            logger.exception("%s is not exists." % manifest_xml)
            raise e

    def get_remote_dict(self):
        for remote in self.remote_list:
            _key = remote.getAttribute("name")
            _value = remote.getAttribute("fetch")
            self.remote_dict[_key] = _value

        return self.remote_dict

    def get_project_list(self, manifest_xml):
        try:
            dom = minidom.parse(manifest_xml)
            root = dom.documentElement

            project_list = root.getElementsByTagName("project")
            self.project_list.extend(project_list)

            include_list = root.getElementsByTagName("include")
            for include in include_list:
                include_manifest_xml = include.getAttribute("name")
                self.get_project_list(os.path.join(os.path.dirname(manifest_xml), include_manifest_xml))
        except IOError as e:
            logger.exception("%s is not exists." % manifest_xml)
            raise e

    def get_project_path_list(self):
        """
        Description:
            get all project path list in manifests file.
        Return: (list) project path list.
        """
        _project_path_list = list()

        for project in self.project_list:
            _project_path_list.append(project.getAttribute("path"))

        return _project_path_list

    def get_project_name_list(self):
        """
        Description:
            get all project name list in manifests file.
        Return: (list) project name list.
        """
        _project_name_list = list()

        for project in self.project_list:
            _project_name_list.append(project.getAttribute("name"))

        return _project_name_list

    def get_project_name(self, project_path):
        """
        Description:
            get project name by project path in manifests file.
        Parameters:
            project_path: (str) project path.
        Return: (str) project name.
        """
        _project_name = str()

        for project in self.project_list:
            if project.getAttribute("path") == project_path:
                return project.getAttribute("name")

        return _project_name

    def get_project_path(self, project_name):
        """
        Description:
            get project path by project name in manifests file.
        Parameters:
            project_name: (str) project name.
        Return: (str) project path.
        """
        _project_path = str()

        for project in self.project_list:
            if project.getAttribute("name") == project_name:
                return project.getAttribute("path")

        return _project_path
