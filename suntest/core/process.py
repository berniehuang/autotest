# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: process.py
# Author:   huangbin@pset.suntec.net
# Date:     2017.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import logging
import psutil

logger = logging.getLogger(__name__)


def get_pid_list(process_name):
    process_name_pids = list()

    pids = psutil.pids()
    for pid in pids:
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess as e:
            logger.error("没有这个进程 %d" % pid)
            continue
        if p.name() == process_name:
            process_name_pids.append(pid)

    return process_name_pids
