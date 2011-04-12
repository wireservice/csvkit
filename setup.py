#!/usr/bin/env python

from setuptools import setup

setup(
    name='csvkit',
    version='0.0.1',
    description='A library of utilities for working with CSV, the king of tabular file formats.',
    author='Christopher Groskopf',
    author_email='staringmonkey@gmail.com',
    url='http://blog.apps.chicagotribune.com/',
    license='MIT',
    packages=[
        'csvkit', 
        'csvkit.convert'
    ],
    scripts = [
        'in2csv',
        'csvcut',
        'csvsql',
        'csvclean',
        'csvsummary',
        'csvlook',
        'csvjoin'
    ],
    install_requires = [
        'argparse==1.2.1',
        'nose==1.0.0',
        'xlrd==0.7.1',
        'python-dateutil==1.5',
        'sqlalchemy==0.6.6']
)
