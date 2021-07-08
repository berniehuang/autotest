# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: uncovr.py
# Author:   huangbin@pset.suntec.net
# Date:     2019.12.11
# ------------------------------------------------------------------------------
import os
import sys
import re
import time
import argparse
import zipfile
import pandas as pd
import numpy as np
import xml.dom.minidom as minidom
from suntest.config import settings
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from itertools import groupby
import logging

logger = logging.getLogger(__name__)


def zip_files(filename_list, zip_name):
    zip = zipfile.ZipFile( zip_name, 'w', zipfile.ZIP_DEFLATED )
    for filename in filename_list:
        logger.debug('压缩文件%s' % filename)
        zip.write(filename)

    zip.close()
    logger.info('压缩文件完成。')


def get_groupby_num_list(num_list):
    groupby_num_list = list()

    fun = lambda x: x[1]-x[0]
    for k, g in groupby(enumerate(num_list), fun):
        l1 = [j for i, j in g]
        groupby_num_list.append(l1)

    return groupby_num_list


def read_source_file(source_file):
    contents = str()

    try:
        with open(source_file, "ro") as fb:
            contents = fb.readlines()
    except Exception as e:
        print(e)
    finally:
        return contents


def get_hit_line_source_code(hit_lines, contents, source_file):
    hit_lines = sorted(hit_lines)
    if hit_lines[-1] > len(contents):
        logger.error("统计行数%s已经超过了源文件%s总行数%d." % (hit_lines[-1], source_file, len(contents)))
        return str()
    hit_indexs = [int(hit_line) - 1 for hit_line in hit_lines]

    try:
        for hit_index in hit_indexs:
            if "<<<" in contents[hit_index]:
                continue
            contents[hit_index] = "<<<  " + contents[hit_index]
    except Exception as e:
        print(e)

    hit_min_index = hit_indexs[0]
    hit_max_index = hit_indexs[len(hit_indexs) - 1]
    source_code = str('\n'.join(contents[(hit_min_index - 5):(hit_max_index + 5)]))

    return source_code


def parse_coverage_xml_report(coverage_report):
    logger.info("开始解析覆盖率报告%s." % coverage_report)
    condition_coverage_hit_record = dict()
    condition_coverage_data_item = tuple()
    line_coverage_hit_record = dict()
    line_coverage_data_item = tuple()
    condition_coverage_data_list = list()
    line_coverage_data_list = list()
    condition_coverage_data_head = ["source_file", "source_code", "condition_coverage", "line_number"]
    line_coverage_data_head = ["source_file", "source_code", "line_number"]
    condition_coverage_df = pd.DataFrame()
    line_coverage_df = pd.DataFrame()

    if not os.path.exists(coverage_report):
        logger.error("覆盖率报告%s不存在。" % coverage_report)
        return (condition_coverage_df, line_coverage_df)

    try:
        tree = ET.parse(coverage_report)
        root = tree.getroot()
        sources = root.find("sources")
        source = sources.find("source")
        repository = source.text
        packages = root.find("packages")
        for package in packages.findall("package"):
            classes = package.find("classes")
            for class_element in classes.findall("class"):
                filename = class_element.get("filename")
                lines = class_element.find("lines")
                for line in lines.findall("line"):
                    source_file = source_file_rmI = os.path.join(repository, filename)
                    # bug of jacoco report xml
                    if re.search(r'I*.java', os.path.basename(source_file)):
                        source_file_rmI = os.path.join(os.path.dirname(source_file), os.path.basename(source_file)[1:])
                    if  not os.path.exists(source_file_rmI) and not os.path.exists(source_file):
                        logger.error("源代码文件%s不存在。" % source_file)
                        continue
                    if line.get("branch") == "true":
                        condition_coverage = line.get("condition-coverage")
                        line_number = int(line.get("number"))
                        if condition_coverage.find("100%"):
                            contents = read_source_file(source_file)
                            source_code = get_hit_line_source_code([line_number], contents, source_file)
                            condition_coverage_data_item = (source_file, source_code, condition_coverage, line_number)
                            condition_coverage_data_list.append(condition_coverage_data_item)
                    if line.get("hits") == "0":
                        line_number = int(line.get("number"))
                        if source_file not in line_coverage_hit_record.keys():
                            line_coverage_hit_record[source_file] = list()
                        line_coverage_hit_record[source_file].append(line_number)
    except Exception as e:
        logger.exception("解析覆盖率报告发生异常%s" % e)
        return (condition_coverage_df, line_coverage_df)

    for source_file,hit_lines in line_coverage_hit_record.items():
        groupby_hit_lines = get_groupby_num_list(hit_lines)
        contents = read_source_file(source_file)
        for lines in groupby_hit_lines:
            source_code = get_hit_line_source_code(lines, contents, source_file)
            line_coverage_data_item = (source_file, source_code, lines)
            line_coverage_data_list.append(line_coverage_data_item)

    if condition_coverage_data_list:
        condition_coverage_df = pd.DataFrame.from_records(condition_coverage_data_list, columns=condition_coverage_data_head)
    else:
        logger.error("未覆盖条件覆盖率数据为空.")

    if line_coverage_data_list:
        line_coverage_df = pd.DataFrame.from_records(line_coverage_data_list, columns=line_coverage_data_head)
    else:
        logger.error("未覆盖行覆盖率数据为空.")

    return (condition_coverage_df, line_coverage_df)


def generate_coverage_xls_report(report, condition_coverage_df, line_coverage_df):
    writer = pd.ExcelWriter(report, engine='xlsxwriter')
    condition_coverage_df.to_excel(writer, sheet_name='Condition', index=False)
    line_coverage_df.to_excel(writer, sheet_name='Line', index=False)

    workbook  = writer.book
    head_format = workbook.add_format({'align': 'center', 'bold': 1})
    source_file_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': 0})
    source_code_format = workbook.add_format({'align': 'left', 'text_wrap': 1 })
    condition_coverage_format = line_number_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap' : 1, 'bold': 0})

    worksheet = writer.sheets['Condition']

    # source_file
    worksheet.set_column('A:A', 70, condition_coverage_format)
    # source_code
    worksheet.set_column('B:B', 100, source_code_format)
    # condition_coverage
    worksheet.set_column('C:C', 20, condition_coverage_format)
    # line_number
    worksheet.set_column('D:D', 14, line_number_format)


    worksheet = writer.sheets['Line']

    # source_file
    worksheet.set_column('A:A', 70, source_file_format)
    # source_code
    worksheet.set_column('B:B', 100, source_code_format)
    # line_number
    worksheet.set_column('C:C', 14, line_number_format)

    try:
        default_encoding = sys.getdefaultencoding()
        if default_encoding != settings.encode:
            reload(sys)
            sys.setdefaultencoding(settings.encode)
        writer.save()
    except UnicodeDecodeError as e:
        logger.exception(e)
    finally:
        reload(sys)
        sys.setdefaultencoding(default_encoding)


def capture_uncovered_code(coverage_xml_report, uncovr_report):
    logger.info("开始生成未覆盖代码抽出报告。")
    (condition_coverage_df, line_coverage_df) = parse_coverage_xml_report(coverage_xml_report)
    generate_coverage_xls_report(uncovr_report, condition_coverage_df, line_coverage_df)

    return True
