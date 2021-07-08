# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: exceptions.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import logging

import suntest.files.read as Read
from suntest.config import settings

logger = logging.getLogger(__name__)


class SuntestError(BaseException):
    """general custom exception"""
    def __init__(self, error_log):
        logger.error(error_log)


class SuntestRunError(SuntestError):
    """run custom exception"""
    def exceptionhandler(self, device, entry):
        try:
            if not device.check_path_exist(settings.tombstone_path):
                return False

            if device.pull_file_from_device(settings.tombstone_path, settings['workspace']):
                tombstone_workspace_path = os.path.join(settings['workspace'], os.path.basename(settings.tombstone_path))
                for tombstone_file in os.listdir(tombstone_workspace_path):
                        with open(os.path.join(tombstone_workspace_path, tombstone_file), 'r') as f:
                            content = f.read()
                            if content.find(entry) is not -1:
                                Read.display_file(os.path.join(tombstone_workspace_path, tombstone_file), "墓碑文件")
                                break
                        f.close()
                        continue
        except Exception as e:
            logger.exception("异常处理发生异常: %s." % e)
            return False


class NoAnyProject(SuntestError):
    """no any project in solution"""
    pass


class SegmentationFault(SuntestRunError):
    """a segmentation error occurred while the program was running"""
    pass


class PushFileFailure(SuntestError):
    """failed to push file to device"""
    pass


class InstallPackageFailure(SuntestError):
    """failed to install package on device"""
    pass


class UninstallPackageFailure(SuntestError):
    """failed to uninstall package on device"""
    pass


class RunOtherError(SuntestRunError):
    """the unittest program run other error"""
    pass


class Timeout(SuntestRunError):
    """the unittest program timeout exception"""
    pass

class OutputTimeout(Timeout):
    """when the unittest program runs, that does not have any output timeout"""
    pass


class RuncaseTimeout(Timeout):
    """the unittest program runtime timeout"""
    pass


class PackagemanagerNoReady(SuntestError):
    """service packagemanager not ready"""
    pass


class InstallAppPackageFailure(SuntestError):
    """install cpk failure"""
    pass


class ProjectConfigNotExist(SuntestError):
    """project.conf is not exists"""
    pass


class PullGcdaFilesFailure(SuntestError):
    """pull gcda files from device failure"""
    pass


class GcnoGeneratePathNoFound(SuntestError):
    """failed to get gcno generate path"""
    pass


class DeviceStartupFailure(SuntestError):
    """failed to startup device"""
    pass


class TrackProgramFailure(SuntestError):
    """failed to track program"""
    pass


class MorethanOneDevice(SuntestError):
    """more than one device"""
    pass


class NoLunchCombo(SuntestError):
    """no lunch combo"""
    pass


class NoInstallLcov(SuntestError):
    """no install lcov"""
    pass


class NoInstallGcovr(SuntestError):
    """no install gcovr"""
    pass


class UnknowDeviceType(SuntestError):
    """unknow device type"""
    pass


class CompileError(SuntestError):
    """compile error"""
    pass


class AvdNameNotSet(SuntestError):
    """avd name not set exception"""
    pass


class TestReportError(SuntestError):
    """test result report exception"""
    pass


class CoverageReportError(SuntestError):
    """coverage report exception"""
    pass


class ProjectConfigNoExist(SuntestError):
    """project config file not exists"""
    pass


class AnotherFailure(SuntestError):
    """other exception"""
    pass
