# -*- coding: UTF-8 -*-
__version__ = '3.9.0'


class ExitStatus(object):
    """Exit status code constants."""
    OK = 0

    EXCEPTION = 1
    CASE_FAILURE = 2
    PUSH_FAILURE = 3
    SEGMENT_FAULT = 4
    OUTPUT_TIMEOUT = 5
    RUN_TIMEOUT = 6
    DEVICE_STARTUP_FAILED = 7
    COMPILE_ERROR = 8
    OTHER_RUN_ERROR = 9
    TEST_REPORT_NOT_FOUND = 10
    COVERAGE_REPORT_NOT_FOUND = 11
    OTHER_ERROR = 12
    NO_MEET_TEST = 13
    INSTALL_FAILURE = 14
    UNINSTALL_FAILURE = 15
    COMPILE_EMU_ERROR = 16
    DEVICE_STATE_OFFLINE = 101
    DEVICE_PROCESS_LACK = 102
    DEVICE_LOG_LACK = 103
    DEVICE_PROP_ERROR = 104

    EXIT_STATUS_CHN = {
        OK: "测试成功",
        EXCEPTION: "其他异常",
        CASE_FAILURE: "测试用例失败",
        PUSH_FAILURE:"推送文件失败",
        SEGMENT_FAULT: "段错误",
        OUTPUT_TIMEOUT: "测试用例超时",
        RUN_TIMEOUT: "测试运行超时",
        DEVICE_STARTUP_FAILED: "设备启动失败",
        COMPILE_ERROR: "编译错误",
        OTHER_RUN_ERROR: "其他运行错误",
        TEST_REPORT_NOT_FOUND: "结果报告不存在",
        COVERAGE_REPORT_NOT_FOUND: "覆盖率报告不存在",
        OTHER_ERROR: "其他错误",
        NO_MEET_TEST: "没有满足条件的测试",
        INSTALL_FAILURE: "安装包失败",
        UNINSTALL_FAILURE: "卸载包失败",
        COMPILE_EMU_ERROR: "编译模拟器错误",
        DEVICE_STATE_OFFLINE: "设备状态检查失败",
        DEVICE_PROCESS_LACK: "设备启动进程检查失败",
        DEVICE_LOG_LACK: "设备启动日志检查失败",
        DEVICE_PROP_ERROR: "设备启动属性错误"
    }
