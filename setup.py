#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = [
    'xlrd>=0.7.1',
    'python-dateutil>=1.5',
    'sqlalchemy>=0.6.6',
    'openpyxl>=1.5.7',
    'dbf==0.94.003']

if sys.version_info < (2, 7):
    install_requires.append('argparse>=1.2.1')

setup(
    name='csvkit',
    version='0.7.3',
    description='A library of utilities for working with CSV, the king of tabular file formats.',
    long_description=open('README').read(),
    author='Christopher Groskopf',
    author_email='staringmonkey@gmail.com',
    url='http://csvkit.rtfd.org/',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    packages=[
        'csvkit',
        'csvkit.convert',
        'csvkit.utilities'
    ],
    entry_points ={
        'console_scripts': [
            'csvclean = csvkit.utilities.csvclean:launch_new_instance',
            'csvcut = csvkit.utilities.csvcut:launch_new_instance',
            'csvgrep = csvkit.utilities.csvgrep:launch_new_instance',
            'csvjoin = csvkit.utilities.csvjoin:launch_new_instance',
            'csvjson = csvkit.utilities.csvjson:launch_new_instance',
            'csvlook = csvkit.utilities.csvlook:launch_new_instance',
            'csvpy = csvkit.utilities.csvpy:launch_new_instance',
            'csvsort = csvkit.utilities.csvsort:launch_new_instance',
            'csvsql = csvkit.utilities.csvsql:launch_new_instance',
            'csvstack = csvkit.utilities.csvstack:launch_new_instance',
            'csvstat = csvkit.utilities.csvstat:launch_new_instance',
            'in2csv = csvkit.utilities.in2csv:launch_new_instance',
            'sql2csv = csvkit.utilities.sql2csv:launch_new_instance'
        ]
    },
    install_requires = install_requires
)
