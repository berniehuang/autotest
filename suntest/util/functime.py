# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: time.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------
import os
import csv
import time


def funcExecTime(func):
    def newFunc(*args, **args2):
        def duration_record_csv(task_name, duration):
            headers = ["task_name", "duration"]
            rows = ['%s' % task_name, '%s' % duration]

            if not os.path.exists('duration.csv'):
                with open('duration.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

            with open ('duration.csv', 'a+') as f:
                writer = csv.writer(f)
                writer.writerow(rows)
  
        t0 = time.time()
        # print "[%s] start: %s" % (func.__name__, time.strftime("%X", time.localtime()))
        back = func(*args, **args2)
        # print "[%s] end: %s" % (func.__name__, time.strftime("%X", time.localtime()))
        duration = time.time() - t0
        print "[TIME] 时长%s %.3f秒" % (func.__name__, duration)
        duration_record_csv(func.__name__, "%.3f" % duration)
        return back
    return newFunc


def get_current_time():
    return "%s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
