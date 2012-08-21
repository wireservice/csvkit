#!/usr/bin/env python

from setuptools import setup

setup(
    name='csvkit',
    version='0.5.0',
    description='A library of utilities for working with CSV, the king of tabular file formats.',
    long_description=open('README').read(),
    author='Christopher Groskopf',
    author_email='staringmonkey@gmail.com',
    url='http://blog.apps.chicagotribune.com/',
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
            'csvcut = csvkit.utilities.csvcut:launch_new_instance',
            'in2csv = csvkit.utilities.in2csv:launch_new_instance',
            'csvsql = csvkit.utilities.csvsql:launch_new_instance',
            'csvclean = csvkit.utilities.csvclean:launch_new_instance',
            'csvstat = csvkit.utilities.csvstat:launch_new_instance',
            'csvlook = csvkit.utilities.csvlook:launch_new_instance',
            'csvjoin = csvkit.utilities.csvjoin:launch_new_instance',
            'csvstack = csvkit.utilities.csvstack:launch_new_instance',
            'csvsort = csvkit.utilities.csvsort:launch_new_instance',
            'csvgrep = csvkit.utilities.csvgrep:launch_new_instance',
            'csvjson = csvkit.utilities.csvjson:launch_new_instance',
            'csvpy = csvkit.utilities.csvpy:launch_new_instance'
        ]
    },
    install_requires = [
        'argparse==1.2.1',
        'xlrd==0.7.1',
        'python-dateutil==1.5',
        'sqlalchemy==0.6.6',
        'openpyxl==1.5.7',
        'dbf==0.94.003']
)
