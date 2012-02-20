#!/usr/bin/env python

from setuptools import setup

setup(
    name='csvkit',
    version='0.4.3',
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
    scripts = [
        'in2csv',
        'csvcut',
        'csvsql',
        'csvclean',
        'csvstat',
        'csvlook',
        'csvjoin',
        'csvstack',
        'csvsort',
        'csvgrep',
        'csvjson'
    ],
    install_requires = [
        'argparse==1.2.1',
        'xlrd==0.7.1',
        'python-dateutil==1.5',
        'sqlalchemy==0.6.6',
        'openpyxl==1.5.7']
)
