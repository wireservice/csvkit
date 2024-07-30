from setuptools import find_packages, setup

with open('README.rst') as f:
    long_description = f.read()

bins = (
    'csvclean',
    'csvcut',
    'csvformat',
    'csvgrep',
    'csvjoin',
    'csvjson',
    'csvlook',
    'csvpy',
    'csvsort',
    'csvsql',
    'csvstack',
    'csvstat',
    'in2csv',
    'sql2csv',
)

setup(
    name='csvkit',
    version='2.0.1',
    description='A suite of command-line tools for working with CSV, the king of tabular file formats.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Christopher Groskopf and James McKinney',
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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
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
            f'{bin} = csvkit.utilities.{bin}:launch_new_instance'
            for bin in bins
        ],
    },

    # https://stackoverflow.com/a/49501350/718180
    data_files=[
        ('share/man/man1', [f'man/{bin}.1'])
        for bin in bins
    ],

    install_requires=[
        'agate>=1.12.0',
        'agate-excel>=0.4.0',
        'agate-dbf>=0.2.3',
        'agate-sql>=0.7.0',
        'openpyxl',
        'sqlalchemy',
        'xlrd',
        # “selectable” entry points were introduced in Python 3.10.
        # https://docs.python.org/3/library/importlib.metadata.html
        'importlib_metadata; python_version < "3.10"',
    ],
    extras_require={
        'zstandard': [
            'zstandard',
        ],
        'test': [
            'coverage>=4.4.2',
            'pytest',
            'pytest-cov',
        ],
    },
)
