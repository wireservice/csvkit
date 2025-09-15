from collections import namedtuple

VersionInfo = namedtuple('VersionInfo',
                         ['major', 'minor', 'micro', 'releaselevel', 'serial'])

def _make_version_info(version):
    if '-' in version:
        version, releaselevel = version.split('-')
    else:
        releaselevel = ''

    major, minor, micro = map(int, version.split('.'))

    return VersionInfo(major, minor, micro, releaselevel, 0)

version = '2.0.7'
version_info = _make_version_info(version)
