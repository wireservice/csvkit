"""Display the version and commands provided by csvkit."""

import argparse
from importlib.metadata import distribution


def launch_new_instance():
    package = distribution('csvkit')
    commands = sorted(
        entry.name for entry in package.entry_points
        if entry.group == 'console_scripts' and entry.name != 'csvkit'
    )
    parser = argparse.ArgumentParser(
        prog='csvkit',
        description=f'csvkit {package.version} provides the following commands:\n\n'
                    + '\n'.join(f'  - {command}' for command in commands),
        epilog='Run a command directly, for example: csvcut --help',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {package.version}')
    parser.parse_args()
    parser.print_help()
