#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: __main__.py
# Author:   huangbin@pset.suntec.net
# Date:     2014.1.12
# ------------------------------------------------------------------------------
import os
import sys
import argparse

import suntest
from suntest import ExitStatus
from suntest.config import PROJECTS
from suntest.config.configloader import ConfigLoader
from suntest.check.checker import Checker
from suntest.project import ProjectFactory
from suntest.project.project import Project


def main():
    # parse args
    parser = argparse.ArgumentParser(description='这是一个自动化的单体测试编译，运行，收集结果的构建脚本工具。')
    parser.add_argument("-b", "--build", action="store_true", dest="build", default=False, help="编译单体测试程序（已弃用）。")
    parser.add_argument("-c", "--config", action="store", dest="config", default=None, help="指定单体测试仓库配置文件。")
    parser.add_argument("-G", "--gcov", action="store_true", dest="gcov", default=False, help="启用gcov覆盖率统计功能。")
    parser.add_argument("-j", "--jobs", action="store", dest="jobs", help="指定编译用cpu核数。")
    parser.add_argument("-J", "--jacoco", action="store_true", dest="jacoco", default=False, help="启用jacoco覆盖率统计功能。")
    parser.add_argument("-l", "--loglevel", action="store", dest="loglevel", default="INFO", help="指定suntest日志等级[DEBUG, INFO, WARNING, ERROR, CRITICAL].")
    parser.add_argument("-L", "--lcov", action="store_true", dest="lcov", default=False, help="启用lcov覆盖率统计功能。")
    parser.add_argument("-m", "--manifest", action="store", dest="manifest", default=".repo/manifests/default.xml", help="指定manifest文件。")
    parser.add_argument("-n", "--name", action="store", dest="name", default="demo", help="指定本次工程名.")
    parser.add_argument("-p", "--project", action="store", dest="project", default= os.environ.get("PROJECT", ""), help="指定项目名。")
    parser.add_argument("-r", "--repo", action="store", dest="repo", help="指定运行本仓库下所有单体测试程序（已弃用）。")
    parser.add_argument("-s", "--settings", action="store", dest="settings", help="指定单体测试项目配置文件。")
    parser.add_argument("-t", "--type", action="store", dest="type", default='unittest', help="指定本次工程类型")
    parser.add_argument("-v", "--version", action="store_true", dest="version", default=False, help="suntest版本信息。")
    parser.add_argument("-w", "--workspace", action="store", dest="workspace", default="workspace", help="指定本次工程结果存放目录。")
    parser.add_argument("--tasks", action="store", dest="tasks", default=['build'], nargs='+', help="指定本次工程运行的任务列表. \
                                                                                                     任务类型举例：(build, emulator, compile, run, report, clean, clear).")
    parser.add_argument("--product-type", action="store", dest="product", default="full", help="指定产品类型。")
    parser.add_argument("--build-env", action="store", dest="build_env", default="BUILD_COV_INSTRUMENT=True", help="设置编译环境变量。")
    parser.add_argument("--test-type", action="store", dest="test_type", default=None, help="指定运行哪一类型单体测试程序。\
                                                                                             目前支持的测试类型有：(gtest，qtest，qapptest， junit).")
    parser.add_argument("--device-type", action="store", dest="device_type", default=None, help="指定设备类型。")
    parser.add_argument("--install-sdk", action="store", dest="install_sdk", default=None, help="sdk安装路径。")
    parser.add_argument("--logcat", action="store", dest="logcat", default=None, help="指定设备抓取日志标签和等级。")
    parser.add_argument("--report-type", action="store", dest="report_type", default="xml", help="指定单体测试覆盖率报告类型。")
    parser.add_argument("--gcov-filter", action="store", dest="gcov_filter", default=None, help="设置gcov过滤配置文件。")
    parser.add_argument("--gcov-filter-section", action="store", dest="gcov_filter_section", default=None, help="指定gcov过滤配置文件的section选项。")
    parser.add_argument("--exclude-unreachable-branches", action="store_true", dest="exclude_unreachable_branches", default=True, help="添加gcovr工具的排除无法达到分支覆盖率 \
                                                                                                                                统计功能。")
    parser.add_argument("--exclude-throw-branches", action="store_true", dest="exclude_throw_branches", default=True, help="添加gcovr工具的排除异常处理分支覆盖率统计功能。")
    options = parser.parse_args()

    if options.version:
        sys.stdout.write(
            "v%s\n"
            % suntest.__version__)
        return 0

    if options.project == "help":
       sys.stdout.write(PROJECTS)
       return 0

    title = """
                                                    _              _
                                   ___  _   _ _ __ | |_  ___  ___ | |_
                                  ( __|| | | | `_ \|  _|/ _ \( __||  _|
                                   __ \| |_| | || || |_ | __/ __ \| |_
                                  |___/ \___/|_||_| \__|\___||___/ \__|
                                                                                              v%s @Suntec""" % suntest.__version__
    print title

    configloader = ConfigLoader(options)
    configloader.load_logging_config()
    configloader.load_project_config()

    checker = Checker()
    checker.check_env()
    checker.check_lcov()
    checker.check_gcovr()

    project = ProjectFactory.get_project_object(options.type, options.name, options.workspace, options.config, options.tasks)
    project.about()
    for task in project.tasks:
        project.run_task(task)
    project.get_test_result()
    project.print_summary()
    return project.result

if __name__ == '__main__':
    sys.exit(main())
