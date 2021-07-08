# suntest

This is an automated testing framework based on the Python scripting language. The main work of this framework includes compiling the test program and the tested program, checking and starting the device, running the test program, obtaining the report and data file, and analyzing the reason of the analysis error.

## Prepartion

All dependencies are installed by using 'python setup.py install'. We encourage you to use a virtualenv. Check the docs for complete installation and usage instructions.

### Install adb

        $ sudo apt-get install android-tools-adb

### Check Python Version

  It is recommended to install Python 2.7 and later version.

### Project config file

  copy project.conf file to workspace.

## Installation
suntest requires Python 2.7 and later version to run.

Unbuntu system provide a package that can be installed using the system package manager.

        $ python setup.py install

## How to use suntest
First, you need to get the complete code for the project.

Second, you have to prepare to run the unittest device, mainly simulators and real machine. The way to get the simulator there are three, the first one is from the daily release version of the simulator server, the second is fully compiled code, the last one is compile sdk.

Third, you have to confirm that there has been a unittest configuration file in tested repository. If not, please refer to the wiki to write the configuration file.

Finally, run the command to run the program.

        $ suntest -r repository --gcov --lcov --loglevel=DEBUG
If you want more information about the suntest command-line parameters, please run the following command.

        $ suntest -h

## suntest Design Class Intro
> The design of the test framework is mainly a solution to manage multiple projects, each project can test one or more warehouse tests, and finally the results of each warehouse summary to the project, the results of each project to the solution, To get the results of this test.

### Solution

A solution which will have several projects, each project can be different types of test items. The solution is used to add, delete, manage, run and count all projects. The load_config method of Solution is used to load log configure file to set log setting.

### Project

class project Mainly responsible for the test case to add, management, equipment startup, inspection, management and closure of the test program to compile, run, access to data files and reports.

### ProjectFactory

The base class for the project factory class, responsible for providing the project class initialization object.

### ProjectUnitTest

Class ProjectUnitTest is mainly reponsible for the unittest to build, management and get report. googletest, qt test and qt app test are supported in the project. we can get the result and the coverage of the unittest by attributes result_info and coverage_info.

### ProjectUnitTestFactory

The class for the project unittest factory class, responsible for providing the project class initialization object.

### Device

This class is the base class for various device classes. Emulator and real machine classes are inherited from it, including the basic operation of the device.

### Emulator

This class is the base class for various emulator classes. EmulatorNativeSDK, EmulatorReleaseSDK and EmulatorRunEmu classes are inherited from it, including the basic operation of the emulator.

### EmulatorNativeSDK

This class is used to start the emulator that is compiled by native_sdk.

### EmulatorReleaseSDK

This class is used to start the emulator that get from release publish.

### EmulatorRunEmu

This class is used to start the emulator that is compiled complete.

### RealDevice

This class is the base class for various realdevice classes. including the basic operation of the realdevice.

### Adb

This class provides adb tools to connect to the device, push, mount and other operations.

### Test

The class is a test runner is a component which the execution of tests and provides the outcome to the user. 

### Gtest

run google test program

### Qtest

run Qt test program

### QApptest

run Qt App test program

### Gcov

This class methods are mainly responsible for gcov data files handler. 

The gcno files that we compiled tested program and the gcda files that we run the test program in the device are copied to the same path, and matched with gcno files and gcda files and delete redundant files.

### GcovReport

After test program run successfully, we get the gcov date files by the methods of the Gcov class. This class is used to generate and parse code coverage xml reports of the unittest with gcov data files by gcovr tool. 

### LcovReport

If users want to read coverage data of the unittest by browser, this class is used to generate and parse lcov data files to generate code coverage html reports of the unittest by lcov.

### ResultReport

After test program generate code result xml report, this class is used to parses the report to get the data of result. sometimes we need to merge multiple reports of the same type by the class methods.
