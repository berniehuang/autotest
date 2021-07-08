import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('suntest/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name = "Suntest",
    version = version,
    author = "huangbin",
    author_email='huangbin@pset.suntec.net',
    description = 'The Unittest framework of Suntec corporation.',
    packages = find_packages(),
    package_data = {
        'suntest': ['config/*.yaml', 'config/*.conf', 'tools/*.jar'],
    },

    entry_points = {
        'console_scripts': ['suntest = suntest.__main__:main'],
    },
    include_package_data = True,
    exclude_package_data = {'': ['README']},
    #install_requires = ['pyyaml>=3.11', 'psutil>=5.2.1', 'xmltodict>=0.11.0', 'gcovr>=4.2', 'gitpython>=3.0.4', \
    #                    'future>=0.18.2', 'xmltodict>=0.12.0', 'numpy==1.16.5', 'pandas==0.24.2', 'xlsxwriter>=1.2.6'],
    zip_safe=False,
)
