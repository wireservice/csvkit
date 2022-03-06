from setuptools import find_packages, setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='csvkit',
    version='1.0.7',
    description='A suite of command-line tools for working with CSV, the king of tabular file formats.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Christopher Groskopf',
    author_email='chrisgroskopf@gmail.com',
    url='https://github.com/wireservice/csvkit',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://csvkit.readthedocs.io/en/latest/',
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    entry_points={
        'console_scripts': [
            'csvclean = csvkit.utilities.csvclean:launch_new_instance',
            'csvcut = csvkit.utilities.csvcut:launch_new_instance',
            'csvformat = csvkit.utilities.csvformat:launch_new_instance',
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
    install_requires=[
        'agate>=1.6.1',
        'agate-excel>=0.2.2',
        'agate-dbf>=0.2.2',
        'agate-sql>=0.5.3',
        'six>=1.6.1',
    ],
    extras_require={
        'test': [
            'coverage>=4.4.2',
            'pytest',
            'pytest-cov',
            'mock>=1.3.0;python_version<"3"',
        ],
        'docs': [
            'sphinx>=1.0.7',
            'sphinx_rtd_theme',
        ],
    }
)
