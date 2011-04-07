#!/usr/bin/env python

from distutils.core import setup
import subprocess

with open('requirements.txt', 'r') as f:
    packages = f.readlines()

subprocess.call(['easy_install', 'pip'])

for p in packages:
    subprocess.call(['pip', 'install', p])

setup(
    name='csvkit',
    version='0.1.0',
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
        'csvclean',
        'csvsql',
    ],
)
