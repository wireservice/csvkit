#!/usr/bin/env python3
"""Check the MANIFEST.in file in a Python source package for completeness.

This script works by building a source distribution archive (by running
setup.py sdist), then checking the file list in the archive against the
file list in version control (Subversion, Git, Mercurial, Bazaar are
supported).

Since the first check can fail to catch missing MANIFEST.in entries when
you've got the right setuptools version control system support plugins
installed, the script copies all the versioned files into a temporary
directory and builds the source distribution again.  This also avoids issues
with stale egg-info/SOURCES.txt files that may cause files not mentioned in
MANIFEST.in to be included nevertheless.
"""

import argparse
import codecs
import configparser
import fnmatch
import locale
import os
import posixpath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import unicodedata
import zipfile
from contextlib import contextmanager
from typing import List, Optional, Union
from xml.etree import ElementTree as ET


if sys.version_info >= (3, 11):
    import tomllib  # pragma: nocover
else:
    import tomli as tomllib  # pragma: nocover

from setuptools.command.egg_info import translate_pattern


# import distutils after setuptools to avoid a warning
from distutils.text_file import TextFile  # isort:skip


__version__ = '0.51'
__author__ = 'Marius Gedminas <marius@gedmin.as>'
__licence__ = 'MIT'
__url__ = 'https://github.com/mgedmin/check-manifest'


class Failure(Exception):
    """An expected failure (as opposed to a bug in this script)."""


#
# User interface
#

class UI:

    def __init__(self, verbosity=1):
        self.verbosity = verbosity
        self._to_be_continued = False
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    @property
    def quiet(self):
        return self.verbosity < 1

    @property
    def verbose(self):
        return self.verbosity >= 2

    def _check_tbc(self):
        if self._to_be_continued:
            print(file=self.stdout)
            self._to_be_continued = False

    def info(self, message):
        if self.quiet:
            return
        self._check_tbc()
        print(message, file=self.stdout)

    def info_begin(self, message):
        if not self.verbose:
            return
        self._check_tbc()
        print(message, end="", file=self.stdout)
        self._to_be_continued = True

    def info_continue(self, message):
        if not self.verbose:
            return
        print(message, end="", file=self.stdout)
        self._to_be_continued = True

    def info_end(self, message):
        if not self.verbose:
            return
        print(message, file=self.stdout)
        self._to_be_continued = False

    def error(self, message):
        self._check_tbc()
        print(message, file=self.stderr)

    def warning(self, message):
        self._check_tbc()
        print(message, file=self.stderr)


def format_list(list_of_strings):
    return "\n".join("  " + s for s in list_of_strings)


def format_missing(missing_from_a, missing_from_b, name_a, name_b):
    res = []
    if missing_from_a:
        res.append("missing from %s:\n%s"
                   % (name_a, format_list(sorted(missing_from_a))))
    if missing_from_b:
        res.append("missing from %s:\n%s"
                   % (name_b, format_list(sorted(missing_from_b))))
    return '\n'.join(res)


#
# Filesystem/OS utilities
#

class CommandFailed(Failure):
    def __init__(self, command: List[str], status: int, output: str) -> None:
        super().__init__("%s failed (status %s):\n%s" % (
                               command, status, output))


def run(
    command: List[str],
    *,
    encoding: Optional[str] = None,
    decode: bool = True,
    cwd: Optional[str] = None  # Python 3.5 forbids trailing comma here!
) -> Union[str, bytes]:
    """Run a command [cmd, arg1, arg2, ...].

    Returns the output (stdout only).

    Raises CommandFailed in cases of error.
    """
    if not encoding:
        encoding = locale.getpreferredencoding()
    try:
        pipe = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=cwd)
    except OSError as e:
        raise Failure(f"could not run {command}: {e}")
    output, stderr = pipe.communicate()
    status = pipe.wait()
    if status != 0:
        raise CommandFailed(command, status,
                            (output + stderr).decode(encoding, 'replace'))
    if decode:
        return output.decode(encoding)
    return output


@contextmanager
def cd(directory):
    """Change the current working directory, temporarily.

    Use as a context manager: with cd(d): ...
    """
    old_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old_dir)


@contextmanager
def mkdtemp(hint=''):
    """Create a temporary directory, then clean it up.

    Use as a context manager: with mkdtemp('-purpose'): ...
    """
    dirname = tempfile.mkdtemp(prefix='check-manifest-', suffix=hint)
    try:
        yield dirname
    finally:
        rmtree(dirname)


def chmod_plus(path, add_bits):
    """Change a file's mode by adding a few bits.

    Like chmod +<bits> <path> in a Unix shell.
    """
    try:
        os.chmod(path, stat.S_IMODE(os.stat(path).st_mode) | add_bits)
    except OSError:  # pragma: nocover
        pass  # well, we tried


def rmtree(path):
    """A version of rmtree that can deal with read-only files and directories.

    Needed because the stock shutil.rmtree() fails with an access error
    when there are read-only files in the directory on Windows, or when the
    directory itself is read-only on Unix.
    """
    def onerror(func, path, exc_info):
        # Did you know what on Python 3.3 on Windows os.remove() and
        # os.unlink() are distinct functions?
        if func is os.remove or func is os.unlink or func is os.rmdir:
            if sys.platform != 'win32':
                chmod_plus(os.path.dirname(path), stat.S_IWUSR | stat.S_IXUSR)
            chmod_plus(path, stat.S_IWUSR)
            func(path)
        else:
            raise
    shutil.rmtree(path, onerror=onerror)


def copy_files(filelist, destdir):
    """Copy a list of files to destdir, preserving directory structure.

    File names should be relative to the current working directory.
    """
    for filename in filelist:
        destfile = os.path.join(destdir, filename)
        # filename should not be absolute, but let's double-check
        assert destfile.startswith(destdir + os.path.sep)
        destfiledir = os.path.dirname(destfile)
        if not os.path.isdir(destfiledir):
            os.makedirs(destfiledir)
        if os.path.isdir(filename):
            os.mkdir(destfile)
        else:
            shutil.copy2(filename, destfile)


def get_one_file_in(dirname):
    """Return the pathname of the one file in a directory.

    Raises if the directory has no files or more than one file.
    """
    files = os.listdir(dirname)
    if len(files) > 1:
        raise Failure('More than one file exists in %s:\n%s' %
                      (dirname, '\n'.join(sorted(files))))
    elif not files:
        raise Failure('No files found in %s' % dirname)
    return os.path.join(dirname, files[0])


#
# File lists are a fundamental data structure here.  We want them to have
# the following properties:
#
# - contain Unicode filenames (normalized to NFC on OS X)
# - be sorted
# - use / as the directory separator
# - list only files, but not directories
#
# We get these file lists from various sources (zip files, tar files, version
# control systems) and we have to normalize them into our common format before
# comparing.
#


def canonical_file_list(filelist):
    """Return the file list convered to a canonical form.

    This means:

    - converted to Unicode normal form C, when running on Mac OS X
    - sorted alphabetically
    - use / as the directory separator
    - list files but not directories

    Caveat: since it works on file lists taken from archives and such, it
    doesn't know whether a particular filename refers to a file or a directory,
    unless it finds annother filename that is inside the first one.  In other
    words, canonical_file_list() will not remove the names of empty directories
    if those appear in the initial file list.
    """
    names = set(normalize_names(filelist))
    for name in list(names):
        while name:
            name = posixpath.dirname(name)
            names.discard(name)
    return sorted(names)


def get_sdist_file_list(sdist_filename, ignore):
    """Return the list of interesting files in a source distribution.

    Removes extra generated files like PKG-INFO and *.egg-info that are usually
    present only in the sdist, but not in the VCS.

    Supports .tar.gz and .zip sdists.
    """
    return strip_sdist_extras(
        ignore,
        strip_toplevel_name(get_archive_file_list(sdist_filename)))


def get_archive_file_list(archive_filename):
    """Return the list of files in an archive.

    Supports .tar.gz and .zip.
    """
    if archive_filename.endswith('.zip'):
        with zipfile.ZipFile(archive_filename) as zf:
            filelist = zf.namelist()
    elif archive_filename.endswith(('.tar.gz', '.tar.bz2', '.tar')):
        with tarfile.open(archive_filename) as tf:
            # XXX: is unicodify() necessary now that Py2 is no longer supported?
            filelist = map(unicodify, tf.getnames())
    else:
        raise Failure('Unrecognized archive type: %s'
                      % os.path.basename(archive_filename))
    return canonical_file_list(filelist)


def unicodify(filename):
    """Make sure filename is Unicode.

    Because the tarfile module on Python 2 doesn't return Unicode.
    """
    if isinstance(filename, bytes):
        # XXX: Ah, but is it right to use the locale encoding here, or should I
        # use sys.getfilesystemencoding()?  A good question!
        return filename.decode(locale.getpreferredencoding())
    else:
        return filename


def strip_toplevel_name(filelist):
    """Strip toplevel name from a file list.

        >>> strip_toplevel_name(['a', 'a/b', 'a/c', 'a/c/d'])
        ['b', 'c', 'c/d']

        >>> strip_toplevel_name(['a', 'a/', 'a/b', 'a/c', 'a/c/d'])
        ['b', 'c', 'c/d']

        >>> strip_toplevel_name(['a/b', 'a/c', 'a/c/d'])
        ['b', 'c', 'c/d']

    """
    if not filelist:
        return filelist
    prefix = filelist[0]
    # so here's a function we assume / is the directory separator
    if '/' in prefix:
        prefix = prefix.partition('/')[0] + '/'
        names = filelist
    else:
        prefix = prefix + '/'
        names = filelist[1:]
    for name in names:
        if not name.startswith(prefix):
            raise Failure("File doesn't have the common prefix (%s): %s"
                          % (name, prefix))
    return [name[len(prefix):] for name in names if name != prefix]


class VCS:

    def __init__(self, ui):
        self.ui = ui

    @classmethod
    def detect(cls, location):
        return os.path.isdir(os.path.join(location, cls.metadata_name))

    def get_versioned_files(self):
        raise NotImplementedError('this is an abstract method')


class Git(VCS):
    metadata_name = '.git'

    # Git for Windows uses UTF-8 instead of the locale encoding.
    # Git on POSIX systems uses the locale encoding.
    _encoding = 'UTF-8' if sys.platform == 'win32' else None

    @classmethod
    def detect(cls, location):
        # .git can be a file for submodules
        return os.path.exists(os.path.join(location, cls.metadata_name))

    def get_versioned_files(self):
        """List all files versioned by git in the current directory."""
        output = run(
            ["git", "ls-files", "-z", "--recurse-submodules"],
            encoding=self._encoding,
        )
        # -z tells git to use \0 as a line terminator; split() treats it as a
        # line separator, so we always get one empty line at the end, which we
        # drop with the [:-1] slice
        return output.split("\0")[:-1]


class Mercurial(VCS):
    metadata_name = '.hg'

    def get_versioned_files(self):
        """List all files under Mercurial control in the current directory."""
        output = run(['hg', 'status', '-ncamd', '.'])
        return output.splitlines()


class Bazaar(VCS):
    metadata_name = '.bzr'

    @classmethod
    def _get_terminal_encoding(self):
        # Python 3.6 lets us name the OEM codepage directly, which is lucky
        # because it also breaks our old method of OEM codepage detection
        # (PEP-528 changed sys.stdout.encoding to UTF-8).
        try:
            codecs.lookup('oem')
        except LookupError:
            pass
        else:  # pragma: nocover
            return 'oem'
        # Based on bzrlib.osutils.get_terminal_encoding()
        encoding = getattr(sys.stdout, 'encoding', None)
        if not encoding:
            encoding = getattr(sys.stdin, 'encoding', None)
        if encoding == 'cp0':  # "no codepage"
            encoding = None
        # NB: bzrlib falls back on bzrlib.osutils.get_user_encoding(),
        # which is like locale.getpreferredencoding() on steroids, and
        # also includes a fallback from 'ascii' to 'utf-8' when
        # sys.platform is 'darwin'.  This is probably something we might
        # want to do in run(), but I'll wait for somebody to complain
        # first, since I don't have a Mac OS X machine and cannot test.
        return encoding

    def get_versioned_files(self):
        """List all files versioned in Bazaar in the current directory."""
        encoding = self._get_terminal_encoding()
        output = run(['bzr', 'ls', '-VR'], encoding=encoding)
        return output.splitlines()


class Subversion(VCS):
    metadata_name = '.svn'

    def get_versioned_files(self):
        """List all files under SVN control in the current directory."""
        output = run(['svn', 'st', '-vq', '--xml'], decode=False)
        tree = ET.XML(output)
        return sorted(entry.get('path') for entry in tree.findall('.//entry')
                      if self.is_interesting(entry))

    def is_interesting(self, entry):
        """Is this entry interesting?

        ``entry`` is an XML node representing one entry of the svn status
        XML output.  It looks like this::

            <entry path="unchanged.txt">
              <wc-status item="normal" revision="1" props="none">
                <commit revision="1">
                  <author>mg</author>
                  <date>2015-02-06T07:52:38.163516Z</date>
                </commit>
              </wc-status>
            </entry>

            <entry path="added-but-not-committed.txt">
              <wc-status item="added" revision="-1" props="none"></wc-status>
            </entry>

            <entry path="ext">
              <wc-status item="external" props="none"></wc-status>
            </entry>

            <entry path="unknown.txt">
              <wc-status props="none" item="unversioned"></wc-status>
            </entry>

        """
        if entry.get('path') == '.':
            return False
        status = entry.find('wc-status')
        if status is None:
            self.ui.warning(
                'svn status --xml parse error: <entry path="%s"> without'
                ' <wc-status>' % entry.get('path')
            )
            return False
        # For SVN externals we get two entries: one mentioning the
        # existence of the external, and one about the status of the external.
        if status.get('item') in ('unversioned', 'external'):
            return False
        return True


def detect_vcs(ui):
    """Detect the version control system used for the current directory."""
    location = os.path.abspath('.')
    while True:
        for vcs in Git, Mercurial, Bazaar, Subversion:
            if vcs.detect(location):
                return vcs(ui)
        parent = os.path.dirname(location)
        if parent == location:
            raise Failure("Couldn't find version control data"
                          " (git/hg/bzr/svn supported)")
        location = parent


def get_vcs_files(ui):
    """List all files under version control in the current directory."""
    vcs = detect_vcs(ui)
    return canonical_file_list(vcs.get_versioned_files())


def normalize_names(names):
    """Normalize file names."""
    return [normalize_name(name) for name in names]


def normalize_name(name):
    """Some VCS print directory names with trailing slashes.  Strip them.

    Easiest is to normalize the path.

    And encodings may trip us up too, especially when comparing lists
    of files.  Plus maybe lowercase versus uppercase.
    """
    name = os.path.normpath(name).replace(os.path.sep, '/')
    name = unicodify(name)  # XXX is this necessary?
    if sys.platform == 'darwin':
        # Mac OS X may have problems comparing non-ASCII filenames, so
        # we convert them.
        name = unicodedata.normalize('NFC', name)
    return name


#
# Packaging logic
#

class IgnoreList:

    def __init__(self):
        self._regexps = []

    @classmethod
    def default(cls):
        return (
            cls()
            # these are always generated
            .global_exclude('PKG-INFO')
            .global_exclude('*.egg-info/*')
            # setup.cfg is always generated, but sometimes also kept in source control
            .global_exclude('setup.cfg')
            # it's not a problem if the sdist is lacking these files:
            .global_exclude(
                '.hgtags', '.hgsigs', '.hgignore', '.gitignore', '.bzrignore',
                '.gitattributes',
            )
            # GitHub template files
            .prune('.github')
            # we can do without these in sdists
            .global_exclude('.circleci/config.yml')
            .global_exclude('.gitpod.yml')
            .global_exclude('.travis.yml')
            .global_exclude('Jenkinsfile')
            # It's convenient to ship compiled .mo files in sdists, but they
            # shouldn't be checked in, so don't complain that they're missing
            # from VCS
            .global_exclude('*.mo')
        )

    def clear(self):
        self._regexps = []

    def __repr__(self):
        return 'IgnoreList(%r)' % (self._regexps)

    def __eq__(self, other):
        return isinstance(other, IgnoreList) and self._regexps == other._regexps

    def __iadd__(self, other):
        assert isinstance(other, IgnoreList)
        self._regexps += other._regexps
        return self

    def _path(self, path):
        return path.replace('/', os.path.sep)

    def exclude(self, *patterns):
        for pat in patterns:
            pat = self._path(pat)
            self._regexps.append(translate_pattern(pat))
        return self

    def global_exclude(self, *patterns):
        for pat in patterns:
            pat = os.path.join('**', self._path(pat))
            self._regexps.append(translate_pattern(pat))
        return self

    def recursive_exclude(self, dirname, *patterns):
        dirname = self._path(dirname)
        for pat in patterns:
            pat = os.path.join(dirname, '**', self._path(pat))
            self._regexps.append(translate_pattern(pat))
        return self

    def prune(self, subdir):
        pat = os.path.join(self._path(subdir), '**')
        self._regexps.append(translate_pattern(pat))
        return self

    def filter(self, filelist):
        return [name for name in filelist
                if not any(rx.match(self._path(name)) for rx in self._regexps)]


WARN_ABOUT_FILES_IN_VCS = [
    # generated files should not be committed into the VCS
    'PKG-INFO',
    '*.egg-info',
    '*.mo',
    '*.py[co]',
    '*.so',
    '*.pyd',
    '*~',
    '.*.sw[po]',
    '.#*',
]

SUGGESTIONS = [(re.compile(pattern), suggestion) for pattern, suggestion in [
    # regexp -> suggestion
    ('^([^/]+[.](cfg|ini))$',       r'include \1'),
    ('^([.]travis[.]yml)$',         r'include \1'),
    ('^([.]coveragerc)$',           r'include \1'),
    ('^([A-Z]+)$',                  r'include \1'),
    ('^(Makefile)$',                r'include \1'),
    ('^[^/]+[.](txt|rst|py)$',      r'include *.\1'),
    ('^([a-zA-Z_][a-zA-Z_0-9]*)/'
     '.*[.](py|zcml|pt|mako|xml|html|txt|rst|css|png|jpg|dot|po|pot|mo|ui|desktop|bat)$',
                                    r'recursive-include \1 *.\2'),
    ('^([a-zA-Z_][a-zA-Z_0-9]*)(?:/.*)?/(Makefile)$',
                                    r'recursive-include \1 \2'),
    # catch-all rules that actually cover some of the above; somewhat
    # experimental: I fear false positives
    ('^([a-zA-Z_0-9]+)$',           r'include \1'),
    ('^[^/]+[.]([a-zA-Z_0-9]+)$',   r'include *.\1'),
    ('^([a-zA-Z_][a-zA-Z_0-9]*)/.*[.]([a-zA-Z_0-9]+)$',
                                    r'recursive-include \1 *.\2'),
]]

CFG_SECTION_CHECK_MANIFEST = 'check-manifest'
CFG_IGNORE_DEFAULT_RULES = (CFG_SECTION_CHECK_MANIFEST, 'ignore-default-rules')
CFG_IGNORE = (CFG_SECTION_CHECK_MANIFEST, 'ignore')
CFG_IGNORE_BAD_IDEAS = (CFG_SECTION_CHECK_MANIFEST, 'ignore-bad-ideas')


def read_config():
    """Read configuration from file if possible."""
    ignore = IgnoreList.default()
    ignore_bad_ideas = IgnoreList()
    config = _load_config()
    if config.get(CFG_IGNORE_DEFAULT_RULES[1], False):
        ignore.clear()
    if CFG_IGNORE[1] in config:
        for p in config[CFG_IGNORE[1]]:
            if p:
                ignore.global_exclude(p)
    if CFG_IGNORE_BAD_IDEAS[1] in config:
        for p in config[CFG_IGNORE_BAD_IDEAS[1]]:
            if p:
                ignore_bad_ideas.global_exclude(p)
    return ignore, ignore_bad_ideas


def _load_config():
    """Searches for config files, reads them and returns a dictionary

    Looks for a ``check-manifest`` section in ``pyproject.toml``,
    ``setup.cfg``, and ``tox.ini``, in that order.  The first file
    that exists and has that section will be loaded and returned as a
    dictionary.

    """
    if os.path.exists("pyproject.toml"):
        with open('pyproject.toml', 'rb') as f:
            config = tomllib.load(f)
        if CFG_SECTION_CHECK_MANIFEST in config.get("tool", {}):
            return config["tool"][CFG_SECTION_CHECK_MANIFEST]

    search_files = ['setup.cfg', 'tox.ini']
    config_parser = configparser.ConfigParser()
    for filename in search_files:
        if (config_parser.read([filename])
                and config_parser.has_section(CFG_SECTION_CHECK_MANIFEST)):
            config = {}

            if config_parser.has_option(*CFG_IGNORE_DEFAULT_RULES):
                ignore_defaults = config_parser.getboolean(*CFG_IGNORE_DEFAULT_RULES)
                config[CFG_IGNORE_DEFAULT_RULES[1]] = ignore_defaults

            if config_parser.has_option(*CFG_IGNORE):
                patterns = [
                    p.strip()
                    for p in config_parser.get(*CFG_IGNORE).splitlines()
                ]
                config[CFG_IGNORE[1]] = patterns

            if config_parser.has_option(*CFG_IGNORE_BAD_IDEAS):
                patterns = [
                    p.strip()
                    for p in config_parser.get(*CFG_IGNORE_BAD_IDEAS).splitlines()
                ]
                config[CFG_IGNORE_BAD_IDEAS[1]] = patterns

            return config

    return {}


def read_manifest(ui):
    """Read existing configuration from MANIFEST.in.

    We use that to ignore anything the MANIFEST.in ignores.
    """
    if not os.path.isfile('MANIFEST.in'):
        return IgnoreList()
    return _get_ignore_from_manifest('MANIFEST.in', ui)


def _get_ignore_from_manifest(filename, ui):
    """Gather the various ignore patterns from a MANIFEST.in.

    Returns an IgnoreList instance.
    """

    class MyTextFile(TextFile):
        def error(self, msg, line=None):  # pragma: nocover
            # (this is never called by TextFile in current versions of CPython)
            raise Failure(self.gen_error(msg, line))

        def warn(self, msg, line=None):
            ui.warning(self.gen_error(msg, line))

    template = MyTextFile(filename,
                          strip_comments=True,
                          skip_blanks=True,
                          join_lines=True,
                          lstrip_ws=True,
                          rstrip_ws=True,
                          collapse_join=True)
    try:
        lines = template.readlines()
    finally:
        template.close()
    return _get_ignore_from_manifest_lines(lines, ui)


def _get_ignore_from_manifest_lines(lines, ui):
    """Gather the various ignore patterns from a MANIFEST.in.

    'lines' should be a list of strings with comments removed
    and continuation lines joined.

    Returns an IgnoreList instance.
    """
    ignore = IgnoreList()
    for line in lines:
        try:
            cmd, rest = line.split(None, 1)
        except ValueError:
            # no whitespace, so not interesting
            continue
        for part in rest.split():
            # distutils enforces these warnings on Windows only
            if part.startswith('/'):
                ui.warning("ERROR: Leading slashes are not allowed in MANIFEST.in on Windows: %s" % part)
            if part.endswith('/'):
                ui.warning("ERROR: Trailing slashes are not allowed in MANIFEST.in on Windows: %s" % part)
        if cmd == 'exclude':
            ignore.exclude(*rest.split())
        elif cmd == 'global-exclude':
            ignore.global_exclude(*rest.split())
        elif cmd == 'recursive-exclude':
            try:
                dirname, patterns = rest.split(None, 1)
            except ValueError:
                # Wrong MANIFEST.in line.
                ui.warning(
                    "You have a wrong line in MANIFEST.in: %r\n"
                    "'recursive-exclude' expects <dir> <pattern1> <pattern2>..."
                    % line
                )
                continue
            ignore.recursive_exclude(dirname, *patterns.split())
        elif cmd == 'prune':
            ignore.prune(rest)
        # XXX: This ignores all 'include'/'global-include'/'recusive-include'/'graft' commands,
        # which is wrong!  Quoting the documentation:
        #
        #    The order of commands in the manifest template matters: initially,
        #    we have the list of default files as described above, and each
        #    command in the template adds to or removes from that list of
        #    files.
        #           -- https://docs.python.org/3.8/distutils/sourcedist.html#specifying-the-files-to-distribute
    return ignore


def file_matches(filename, patterns):
    """Does this filename match any of the patterns?"""
    return any(fnmatch.fnmatch(filename, pat)
               or fnmatch.fnmatch(os.path.basename(filename), pat)
               for pat in patterns)


def strip_sdist_extras(ignore, filelist):
    """Strip generated files that are only present in source distributions.

    We also strip files that are ignored for other reasons, like
    command line arguments, setup.cfg rules or MANIFEST.in rules.
    """
    return ignore.filter(filelist)


def find_bad_ideas(filelist):
    """Find files matching WARN_ABOUT_FILES_IN_VCS patterns."""
    return [name for name in filelist
            if file_matches(name, WARN_ABOUT_FILES_IN_VCS)]


def find_suggestions(filelist):
    """Suggest MANIFEST.in patterns for missing files.

    Returns two lists: one with suggested MANIGEST.in commands, and one with
    files for which no suggestions were offered.
    """
    suggestions = set()
    unknowns = []
    for filename in filelist:
        for pattern, suggestion in SUGGESTIONS:
            m = pattern.match(filename)
            if m is not None:
                suggestions.add(pattern.sub(suggestion, filename))
                break
        else:
            unknowns.append(filename)
    return sorted(suggestions), unknowns


def is_package(source_tree='.'):
    """Is the directory the root of a Python package?

    Note: the term "package" here refers to a collection of files
    with a setup.py/pyproject.toml, not to a directory with an __init__.py.
    """
    return (
        os.path.exists(os.path.join(source_tree, 'setup.py'))
        or os.path.exists(os.path.join(source_tree, 'pyproject.toml'))
    )


def extract_version_from_filename(filename):
    """Extract version number from sdist filename."""
    filename = os.path.splitext(os.path.basename(filename))[0]
    if filename.endswith('.tar'):
        filename = os.path.splitext(filename)[0]
    return filename.split('-')[-1]


def should_use_pep_517():
    """Check if the project uses PEP-517 builds."""
    # https://www.python.org/dev/peps/pep-0517/#build-system-table says
    # "If the pyproject.toml file is absent, or the build-backend key is
    # missing, the source tree is not using this specification, and tools
    # should revert to the legacy behaviour of running setup.py".
    if not os.path.exists('pyproject.toml'):
        return False
    with open('pyproject.toml', 'rb') as f:
        config = tomllib.load(f)
    if "build-system" not in config:
        return False
    if "build-backend" not in config["build-system"]:
        return False
    return True


def build_sdist(tempdir, python=sys.executable, build_isolation=True):
    """Build a source distribution in a temporary directory.

    Should be run with the current working directory inside the Python package
    you want to build.
    """
    if should_use_pep_517():
        # I could do this in-process with
        #   import build.__main__
        #   build.__main__.build('.', tempdir)
        # but then it would print a bunch of things to stdout and I'd have to
        # worry about exceptions
        cmd = [python, '-m', 'build', '--sdist', '.', '--outdir', tempdir]
        if not build_isolation:
            cmd.append('--no-isolation')
        run(cmd)
    else:
        run([python, 'setup.py', 'sdist', '-d', tempdir])


def check_manifest(source_tree='.', create=False, update=False,
                   python=sys.executable, ui=None, extra_ignore=None,
                   extra_ignore_bad_ideas=None,
                   build_isolation=True):
    """Compare a generated source distribution with list of files in a VCS.

    Returns True if the manifest is fine.
    """
    if ui is None:
        ui = UI()
    all_ok = True
    if os.path.sep in python:
        python = os.path.abspath(python)
    with cd(source_tree):
        if not is_package():
            raise Failure(
                'This is not a Python project (no setup.py/pyproject.toml).')
        ignore, ignore_bad_ideas = read_config()
        ignore += read_manifest(ui)
        if extra_ignore:
            ignore += extra_ignore
        if extra_ignore_bad_ideas:
            ignore_bad_ideas += extra_ignore_bad_ideas
        ui.info_begin("listing source files under version control")
        all_source_files = get_vcs_files(ui)
        source_files = strip_sdist_extras(ignore, all_source_files)
        ui.info_continue(": %d files and directories" % len(source_files))
        if not all_source_files:
            raise Failure('There are no files added to version control!')
        ui.info_begin("building an sdist")
        with mkdtemp('-sdist') as tempdir:
            build_sdist(tempdir, python=python, build_isolation=build_isolation)
            sdist_filename = get_one_file_in(tempdir)
            ui.info_continue(": %s" % os.path.basename(sdist_filename))
            sdist_files = get_sdist_file_list(sdist_filename, ignore)
            ui.info_continue(": %d files and directories" % len(sdist_files))
            version = extract_version_from_filename(sdist_filename)
        existing_source_files = list(filter(os.path.exists, all_source_files))
        missing_source_files = sorted(set(all_source_files) - set(existing_source_files))
        if missing_source_files:
            ui.warning("some files listed as being under source control are missing:\n%s"
                       % format_list(missing_source_files))
        ui.info_begin("copying source files to a temporary directory")
        with mkdtemp('-sources') as tempsourcedir:
            copy_files(existing_source_files, tempsourcedir)
            for filename in 'MANIFEST.in', 'setup.py', 'pyproject.toml':
                if filename not in source_files and os.path.exists(filename):
                    # See https://github.com/mgedmin/check-manifest/issues/7
                    # and https://github.com/mgedmin/check-manifest/issues/46:
                    # if we do this, the user gets a warning about files
                    # missing from source control; if we don't do this,
                    # things get very confusing for the user!
                    copy_files([filename], tempsourcedir)
            ui.info_begin("building a clean sdist")
            with cd(tempsourcedir):
                with mkdtemp('-sdist') as tempdir:
                    os.environ['SETUPTOOLS_SCM_PRETEND_VERSION'] = version
                    build_sdist(tempdir, python=python, build_isolation=build_isolation)
                    sdist_filename = get_one_file_in(tempdir)
                    ui.info_continue(": %s" % os.path.basename(sdist_filename))
                    clean_sdist_files = get_sdist_file_list(sdist_filename, ignore)
                    ui.info_continue(": %d files and directories" % len(clean_sdist_files))
        missing_from_manifest = set(source_files) - set(clean_sdist_files)
        missing_from_VCS = set(sdist_files + clean_sdist_files) - set(source_files)
        if not missing_from_manifest and not missing_from_VCS:
            ui.info("lists of files in version control and sdist match")
        else:
            ui.error(
                "lists of files in version control and sdist do not match!\n%s"
                % format_missing(missing_from_VCS, missing_from_manifest, "VCS", "sdist"))
            suggestions, unknowns = find_suggestions(missing_from_manifest)
            user_asked_for_help = update or (create and not
                                                os.path.exists('MANIFEST.in'))
            if 'MANIFEST.in' not in existing_source_files:
                if suggestions and not user_asked_for_help:
                    ui.info("no MANIFEST.in found; you can run 'check-manifest -c' to create one")
                else:
                    ui.info("no MANIFEST.in found")
            if suggestions:
                ui.info("suggested MANIFEST.in rules:\n%s" % format_list(suggestions))
                if user_asked_for_help:
                    existed = os.path.exists('MANIFEST.in')
                    with open('MANIFEST.in', 'a') as f:
                        if not existed:
                            ui.info("creating MANIFEST.in")
                        else:
                            ui.info("updating MANIFEST.in")
                            f.write('\n# added by check-manifest\n')
                        f.write('\n'.join(suggestions) + '\n')
                    if unknowns:
                        ui.info("don't know how to come up with rules matching\n%s"
                                % format_list(unknowns))
            elif user_asked_for_help:
                ui.info("don't know how to come up with rules matching any of the files, sorry!")
            all_ok = False
        bad_ideas = find_bad_ideas(all_source_files)
        filtered_bad_ideas = ignore_bad_ideas.filter(bad_ideas)
        if filtered_bad_ideas:
            ui.warning(
                "you have %s in source control!\n"
                "that's a bad idea: auto-generated files should not be versioned"
                % filtered_bad_ideas[0])
            if len(filtered_bad_ideas) > 1:
                ui.warning("this also applies to the following:\n%s"
                           % format_list(filtered_bad_ideas[1:]))
            all_ok = False
    return all_ok


#
# Main script
#

def main():
    parser = argparse.ArgumentParser(
        description="Check a Python MANIFEST.in file for completeness")
    parser.add_argument(
        'source_tree', default='.', nargs='?',
        help='location for the source tree (default: .)')
    parser.add_argument(
        '--version', action='version',
        version='%(prog)s version ' + __version__)
    parser.add_argument(
        '-q', '--quiet', action='store_const', dest='quiet',
        const=0, default=1, help='reduced output verbosity')
    parser.add_argument(
        '-v', '--verbose', action='store_const', dest='verbose',
        const=1, default=0, help='more verbose output')
    parser.add_argument(
        '-c', '--create', action='store_true',
        help='create a MANIFEST.in if missing (default: exit with an error)')
    parser.add_argument(
        '-u', '--update', action='store_true',
        help='append suggestions to MANIFEST.in (implies --create)')
    parser.add_argument(
        '-p', '--python', default=sys.executable,
        help=(
            'use this Python interpreter for running setup.py sdist'
            ' (default: %(default)s)'
        ))
    parser.add_argument(
        '--ignore', metavar='patterns', default=None,
        help=(
            'ignore files/directories matching these comma-separated'
            ' glob patterns'
        ))
    parser.add_argument(
        '--ignore-bad-ideas', metavar='patterns', default=[],
        help=(
            'ignore bad idea files/directories matching these'
            ' comma-separated glob patterns'
        ))
    parser.add_argument(
        '--no-build-isolation', dest='build_isolation', action='store_false',
        help=(
            'disable isolation when building a modern source distribution'
            ' (default: use build isolation).'
            ' Build dependencies specified by pyproject.toml must be already'
            ' installed if this option is used.'
        ))
    args = parser.parse_args()

    ignore = IgnoreList()
    if args.ignore:
        ignore.global_exclude(*args.ignore.split(','))

    ignore_bad_ideas = IgnoreList()
    if args.ignore_bad_ideas:
        ignore_bad_ideas.global_exclude(*args.ignore_bad_ideas.split(','))

    ui = UI(verbosity=args.quiet + args.verbose)

    try:
        if not check_manifest(args.source_tree, create=args.create,
                              update=args.update, python=args.python,
                              ui=ui, extra_ignore=ignore,
                              extra_ignore_bad_ideas=ignore_bad_ideas,
                              build_isolation=args.build_isolation):
            sys.exit(1)
    except Failure as e:
        ui.error(str(e))
        sys.exit(2)


#
# zest.releaser integration
#

def zest_releaser_check(data):
    """Check the completeness of MANIFEST.in before the release.

    This is an entry point for zest.releaser.  See the documentation at
    https://zestreleaser.readthedocs.io/en/latest/entrypoints.html
    """
    from zest.releaser.utils import ask
    source_tree = data['workingdir']
    if not is_package(source_tree):
        # You can use zest.releaser on things that are not Python packages.
        # It's pointless to run check-manifest in those circumstances.
        # See https://github.com/mgedmin/check-manifest/issues/9 for details.
        return
    if not ask("Do you want to run check-manifest?"):
        return
    ui = UI()
    try:
        if not check_manifest(source_tree, ui=ui):
            if not ask("MANIFEST.in has problems."
                       " Do you want to continue despite that?", default=False):
                sys.exit(1)
    except Failure as e:
        ui.error(str(e))
        if not ask("Something bad happened."
                   " Do you want to continue despite that?", default=False):
            sys.exit(2)


if __name__ == '__main__':
    main()
