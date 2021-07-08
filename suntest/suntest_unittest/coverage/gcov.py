# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: gcov.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import sys
import shutil
import fnmatch
import logging

import suntest.files.copy as Copy
import suntest.files.remove as Remove
from suntest.core import exceptions
from suntest.files.find import find_file_path

logger = logging.getLogger(__name__)


class Gcov(object):
    def __init__(self, source_code_path, gcno_generate_path, gcda_generate_path, head_generate_path):
        self.source_code_path = source_code_path
        self.gcno_generate_path = gcno_generate_path
        self.gcda_generate_path = gcda_generate_path
        self.head_generate_path = head_generate_path
        self.temp_gcdafile_path = "/tmp/temp_gcdafile"

    def _pull_gcda_files(self, device, remote_path_list):
        """
        Description:
            pull gcda files to the target path.
        Return: (bool)
        Parameters:
            device: (object) the device object.
        """
        logger.debug("开始从设备上拉取gcda文件...")
        pull_gcda_flag = False

        for remote_path in remote_path_list:
            logger.debug("拉取gcda文件从%s到%s." % (remote_path, self.temp_gcdafile_path))
            pull_gcda_flag = device.pull_file_from_device(remote_path, self.temp_gcdafile_path)
            if pull_gcda_flag:
                break

        if pull_gcda_flag:
            logger.info("从设备上拉取gcda文件成功。")
            return True
        else:
            raise exceptions.PullGcdaFilesFailure("从设备上拉取gcda文件失败。")
            return False

    def _copy_gcda_files(self, source_path, target_path):
        """
        Description:
            copy gcda files.
        Return: (bool)
        Parameters:
            source_path: (str) the source path of gcno files.
            target_path: (str) the target path of gcno files.
        """
        logger.debug("拷贝gcda文件从%s到%s。" % (source_path, target_path))

        return Copy.copy_tree_with_fext(source_path, target_path, '.gcda')

    def _copy_gcno_files(self, source_path, target_path):
        """
        Description:
            copy gcno files.
        Return: (bool)
        Parameters:
            source_path: (str) the source path of gcno files.
            target_path: (str) the target path of gcno files.
        """
        logger.debug("拷贝gcno文件从%s到%s。" % (source_path, target_path))

        return Copy.copy_tree_with_fext(source_path, target_path, '.gcno', exclude_dirs=['LINKED', 'PACKED', 'WHOLE'])

    def _copy_head_files(self, source_path, target_path):
        """
        Description:
            copy head files.
        Return: (bool)
        Parameters:
            source_path: (str) the source path of head files.
            target_path: (str) the target path of head files.
        """
        if not source_path or not target_path:
            return False
        if not os.path.exists(source_path) or not os.path.exists(target_path):
            return False

        logger.debug("拷贝头文件从%s到%s." % (source_path, target_path))

        return Copy.copy_tree_with_fext(source_path, target_path, '.h')

    def _match_gcov_files(self, target_path):
        """
        Description:
            match gcno and gcda files.
        Return: (bool)
        Parameters:
            target_path: (str) the target path to match gcov files.
        """
        def get_match_file_list(directory, match_file_format):
            """
            Description:
                get match file format filename list.
            Return: (list) match file list
            Parameters:
                directory: (str) the target path to match file format.
                match_file_format: (str) match file format.
            """
            _match_file_list = list()

            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    if filename.endswith(match_file_format):
                        _match_file_list.append(filename)
                elif os.path.isdir(filepath):
                    sub_match_file_list = get_match_file_list(filepath, match_file_format)
                    _match_file_list.extend(sub_match_file_list)

            return _match_file_list

        def remove_no_match_files(code_file_list, gcov_file_list, target_path):
            """
            Description:
                remove no match gcov files with code files.
            Return: (bool)
            Parameters:
                code_file_list: (list) source code file list.
                gcov_file_list: (list) gcov file list.
                target_path: (str) source code directory.
            """
            _code_file_name_list = [os.path.splitext(code_file)[0] for code_file in code_file_list]

            for gcov_file in gcov_file_list:
                gcov_file_name = os.path.splitext(gcov_file)[0].replace(".cpp", "")
                if gcov_file_name not in _code_file_name_list:
                    gcov_file_path = find_file_path(target_path, gcov_file)
                    if gcov_file_path:
                        logger.debug("删除没有匹配到的gcov文件: %s" % gcov_file_path)
                        os.remove(gcov_file_path)

        logger.debug("在目录%s下匹配gcda文件和gcno文件." % target_path)
        code_file_list = list()
        gcno_file_list = list()
        gcda_file_list = list()

        code_file_list.extend(get_match_file_list(target_path, "cpp"))
        code_file_list.extend(get_match_file_list(target_path, "c"))
        gcno_file_list = get_match_file_list(target_path, "gcno")
        gcda_file_list = get_match_file_list(target_path, "gcda")

        remove_no_match_files(code_file_list, gcno_file_list, target_path)
        remove_no_match_files(code_file_list, gcda_file_list, target_path)

    def assemble_gcov_files(self, device, remote_path_list=[]):
        """
        Description:
            capture gcda and gcno files to source code path
            to build coverage report conveniently by gcovr or lcov.
        Return: (bool)
        Parameters:
            target: (str) the target library or executable program for coverage test.
        """
        remote_path_list = [os.path.join(self.gcda_generate_path, self.gcno_generate_path.strip(os.path.sep)), \
                            os.path.join(self.gcda_generate_path, "release")]

        self._pull_gcda_files(device, remote_path_list)
        self._copy_gcda_files(self.temp_gcdafile_path, self.source_code_path)
        self._copy_gcno_files(self.gcno_generate_path, self.source_code_path)
        self._copy_head_files(self.head_generate_path, self.source_code_path)
        self._match_gcov_files(self.source_code_path)

    def __del__(self):
        try:
            shutil.rmtree(self.temp_gcdafile_path)
        except OSError as e:
            logger.error("gcda文件暂存目录%s不存在。" % self.temp_gcdafile_path)
