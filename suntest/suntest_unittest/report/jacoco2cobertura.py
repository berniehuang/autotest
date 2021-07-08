# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: jacoco2cobertura.py
# Author:   huangbin@iauto.com
# Date:     2019.3.17
# ------------------------------------------------------------------------------
import re
import sys
import os.path
import logging
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from suntest.files.find import find_file_path

logger = logging.getLogger(__name__)


class Jacoco2Cobertura(object):
    def __init__(self, source_root, source_dirs, jacoco_report, cobertura_report):
        """
        Description:
            transfer jacoco coverage xml report to cobertura xml report.
        Parameters:
            source_root: (str) source code directory.
            source_dirs: (list) source code directory for each junit.
            jacoco_report: (str) jacoco code coverage xml report.
            cobertura_report: (str) cobertura coverage xml report.
        """
        self.source_root = source_root
        self.source_dirs = source_dirs
        self.jacoco_report = jacoco_report
        self.cobertura_report = cobertura_report

    def read_jacoco_report(self):
        """
        Description:
            read jacoco xml report.
        Return: (object) Element
        """
        root = ET.Element('root')

        try:
            tree = ET.parse(self.jacoco_report)
            root = tree.getroot()
        except Exception as e:
            logger.exception("Caught unexpected exception: %s\n" % str(e))
        finally:
            return root

    def write_xml_report(self, xmlstr, report):
        """
        Description:
            write xml string in xml format report.
        Return: (bool) if write report success then reutrn true or false
        """
        dom = parseString(xmlstr)
        try:
            with open(report,'w') as f:
                dom.writexml(f, indent='', addindent=' ', newl='\n', encoding='UTF-8')
                return True
        except Exception as e:
            logger.exception("Caught unexpected exception: %s\n" % str(e))
            return False

    def find_lines(self, jacoco_package, filename):
        """
        Description:
            Return all <line> elements for a given source file in a package.
        """
        lines = list()
        sourcefiles = jacoco_package.findall("sourcefile")

        for sourcefile in sourcefiles:
            if sourcefile.attrib.get("name") == os.path.basename(filename):
                lines = lines + sourcefile.findall("line")

        return lines

    def line_is_after(self, jacoco_method, start_line):
        return int(jacoco_method.attrib.get('line', 0)) > start_line

    def method_lines(self, jacoco_method, jacoco_methods, jacoco_lines):
        """
        Description:
            Filter the lines from the given set of jacoco_lines that apply to the given jacoco_method.
        """
        start_line = int(jacoco_method.attrib.get('line', 0))
        larger = list(int(jacoco_method.attrib.get('line', 0)) for jacoco_method in jacoco_methods if self.line_is_after(jacoco_method, start_line))
        end_line = min(larger) if len(larger) else 99999999

        for jacoco_line in jacoco_lines:
            if start_line <= int(jacoco_line.attrib['nr']) < end_line:
                yield jacoco_line

    def guess_filename(self, path_to_class):
        m = re.match('([^$]*)', path_to_class)
        filename = (m.group(1) if m else path_to_class) + '.java'
        for source_dir in self.source_dirs:
            filepath = os.path.join(source_dir, filename)
            if os.path.exists(filepath):
                return filepath.replace(self.source_root, "").strip(os.path.sep)
            else:
                return find_file_path(self.source_root, os.path.basename(filename)).replace(self.source_root, "").strip(os.path.sep)

    def add_counters(self, source, target):
        target.set('line-rate', self.counter(source, 'LINE', self.fraction))
        target.set('lines-covered', self.counter(source, 'LINE', self.covered))
        target.set('lines-valid', self.counter(source, 'LINE', self.sum))
        target.set('branch-rate', self.counter(source, 'BRANCH', self.fraction))
        target.set('branches-covered', self.counter(source, 'BRANCH', self.covered))
        target.set('branches-valid', self.counter(source, 'BRANCH', self.sum))
        target.set('complexity', self.counter(source, 'COMPLEXITY', self.sum))

    def fraction(self, covered, missed):
        return covered / (covered + missed)

    def sum(self, covered, missed):
        return int(covered + missed)

    def covered(self, covered, missed):
        return int(covered)

    def counter(self, source, type, operation):
        counters = source.findall('counter')
        counter = next((counter_type for counter_type in counters if counter_type.attrib.get('type') == type), None)

        if counter is not None:
            covered = float(counter.attrib['covered'])
            missed  = float(counter.attrib['missed'])
            return str(operation(covered, missed))
        else:
            return '0.0'

    def convert_lines(self, jacoco_lines, into):
        """
        Description:
            covert jacoco lines element to cobertura lines element.
        Parameters:
            jacoco_lines: (Element) jacoco lines Element.
        """
        cobertura_lines = ET.SubElement(into, 'lines')

        for jacoco_line in jacoco_lines:
            mb = int(jacoco_line.attrib['mb'])
            cb = int(jacoco_line.attrib['cb'])
            ci = int(jacoco_line.attrib['ci'])

            cobertura_line = ET.SubElement(cobertura_lines, 'line')
            cobertura_line.set('number', jacoco_line.attrib['nr'])
            cobertura_line.set('hits', '1' if ci > 0 else '0') # Probably not true but no way to know from JaCoCo XML file

            if mb + cb > 0:
                percentage = str(int(100 * (float(cb) / (float(cb) + float(mb))))) + '%'
                cobertura_line.set('branch',             'true')
                cobertura_line.set('condition-coverage', percentage + ' (' + str(cb) + '/' + str(cb + mb) + ')')

                condition = ET.SubElement(ET.SubElement(cobertura_line, 'conditions'), 'condition')
                condition.set('number', '0')
                condition.set('type', 'jump')
                condition.set('coverage', percentage)
            else:
                cobertura_line.set('branch', 'false')

    def convert_method(self, jacoco_method, jacoco_lines):
        """
        Description:
            covert jacoco method element to cobertura method element.
        Parameters:
            jacoco_method: (Element) jacoco method Element.
            jacoco_lines: (Element) jacoco lines Element.
        Return: (Element) cobertura method Element.
        """
        cobertura_method = ET.Element('method')

        cobertura_method.set('name', jacoco_method.attrib['name'])
        cobertura_method.set('signature', jacoco_method.attrib['desc'])

        self.add_counters(jacoco_method, cobertura_method)
        self.convert_lines(jacoco_lines, cobertura_method)

        return cobertura_method

    def convert_class(self, jacoco_class, jacoco_package):
        """
        Description:
            covert jacoco class element to cobertura class element.
        Parameters:
            jacoco_class: (Element) jacoco class Element.
            jacoco_package: (Element) jacoco package Element.
        Return: (Element) cobertura class Element.
        """
        cobertura_class = ET.Element('class')

        cobertura_class.set('name', jacoco_class.attrib['name'].replace('/', '.'))
        cobertura_class.set('filename', self.guess_filename(jacoco_class.attrib['name']))

        all_jacoco_lines = list(self.find_lines(jacoco_package, cobertura_class.attrib['filename']))

        cobertura_methods = ET.SubElement(cobertura_class, 'methods')
        all_jacoco_methods = list(jacoco_class.findall('method'))
        for jacoco_method in all_jacoco_methods:
            jacoco_method_lines = self.method_lines(jacoco_method, all_jacoco_methods, all_jacoco_lines)
            cobertura_methods.append(self.convert_method(jacoco_method, jacoco_method_lines))

        self.add_counters(jacoco_class, cobertura_class)
        self.convert_lines(all_jacoco_lines, cobertura_class)

        return cobertura_class

    def convert_package(self, jacoco_package):
        """
        Description:
            covert jacoco package element to cobertura package element.
        Parameters:
            jacoco_package: (Element) jacoco package Element.
        Return: (Element) cobertura package Element.
        """
        cobertura_package = ET.Element('package')

        cobertura_package.attrib['name'] = jacoco_package.attrib['name'].replace('/', '.')

        cobertura_classes = ET.SubElement(cobertura_package, 'classes')
        for jacoco_class in jacoco_package.findall('class'):
            cobertura_classes.append(self.convert_class(jacoco_class, jacoco_package))

        self.add_counters(jacoco_package, cobertura_package)

        return cobertura_package

    def convert_root(self, jacoco_root, source_root):
        """
        Description:
            covert jacoco root element to cobertura root element.
        Parameters:
            jacoco_root: (Element) jacoco root xml Element.
            source_root: (str) source code root.
        """
        cobertura_root = ET.Element('coverage')

        #Andoid9 do not have sessioninfo attr, set 0
        # cobertura_root.set('timestamp', str(int(jacoco_root.find('sessioninfo').attrib['start']) / 1000))
        cobertura_root.set('timestamp', '0')

        sources = ET.SubElement(cobertura_root, 'sources')
        ET.SubElement(sources, 'source').text = source_root

        packages = ET.SubElement(cobertura_root, 'packages')
        for package in jacoco_root.findall('package'):
            packages.append(self.convert_package(package))

        self.add_counters(jacoco_root, cobertura_root)

        return cobertura_root

    def convert_jacoco_report_2_cobertura_report(self):
        """
        Description:
            covert jacoco xml report to cobertura xml report.
        """
        jacoco_root = self.read_jacoco_report()
        cobertura_root = self.convert_root(jacoco_root, self.source_root)

        xmlstr = '<?xml version="1.0" ?>' + ET.tostring(cobertura_root)
        self.write_xml_report(xmlstr, self.cobertura_report)
