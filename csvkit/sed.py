#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A stream-oriented CSV modification tool. Like a stripped-down "sed"
command, but for tabular data.
"""

import re
import subprocess
import sys

from csvkit.exceptions import ColumnIdentifierError

import six

class InvalidModifier(Exception):
    def __init__(self, message):
        super(InvalidModifier, self).__init__('Invalid modifier: %s' % message)

class CSVModifier(six.Iterator):
    """
    On-the-fly modifies CSV records coming from a csvkit reader object.

    :Parameters:

    reader : iter

      The CSV record source - must support the `next()` call, which
      should return a list of values.

    modifiers : { list, dict }

      Specifies a set of modifiers to apply to the `reader`, which can
      be either a sequence or dictionary of modifiers to apply. If
      it is a sequence, then the modifiers are applied to the
      equivalently positioned cells in the input records. If it is a
      dictionary, the keys can be integers (column position) or
      strings (column name). In all cases, the modifiers can be one of
      the following:

      * function : takes a single string argument and returns a string
      * string : a sed-like modifier

      Currently supported modification modifiers:

      * Substitution: "s/REGEX/REPL/FLAGS"

        Replaces regular expression `REGEX` with replacement string
        `REPL`, which can use back references. Supports the following
        flags:

        * i: case-insensitive
        * g: global replacement (otherwise only the first is replaced)
        * l: uses locale-dependent character classes
        * m: enables multiline matching for "^" and "$"
        * s: "." also matches the newline character
        * u: enables unicode escape sequences
        * x: `REGEX` uses verbose descriptors & comments

      * Transliteration: "y/SRC/DST/FLAGS"

        (This is a slightly modified version of sed's "y" command.)

        Each character in `SRC` is replaced with the corresponding
        character in `DST`. The dash character ("-") indicates a range
        of characters (e.g. "a-z" for all alphabetic characters).    If
        the dash is needed literally, then it must be the first or
        last character, or escaped with "\". The "\" character escapes
        itself. Only the "i" flag, indicating case-insensitive
        matching of `SRC`, is supported.

      * Execution: "e/REGEX/COMMAND/FLAGS"

        For cells matching `REGEX`, execute (using bash) the external
        command `COMMAND`, which can back-references to `REGEX`. All
        new lines are stripped in the output of `COMMAND`.

        The following flags are supported for `REGEX`:

        * i: case-insensitive
        * l: uses locale-dependent character classes
        * m: enables multiline matching for "^" and "$"
        * s: "." also matches the newline character
        * u: enables unicode escape sequences
        * x: `REGEX` uses verbose descriptors & comments

      Note that the "/" character can be any character as long as it
      is used consistently and not used within the modifier,
      e.g. ``s|a|b|`` is equivalent to ``s/a/b/``.

    header : bool, optional, default: true

      If truthy (the default), then the first row will not be modified.
    """
    def __init__(self, reader, modifiers, header=True):
        self.reader = reader
        self.header = header
        self.column_names = next(reader) if header else None
        self.modifiers = standardize_modifiers(self.column_names, modifiers)

    def __iter__(self):
        return self

    def __next__(self):
        if self.header:
            self.header = False
            return self.column_names
        row = next(self.reader)
        for col, mod in self.modifiers.items():
            row[col] = mod(row[col])
        return row

def standardize_modifiers(column_names, modifiers):
    """
    Given modifiers in any of the permitted input forms, return a dict whose keys
    are column indices and whose values are functions which return a modified value.
    If modifiers is a dictionary and any of its keys are values in column_names, the
    returned dictionary will have those keys replaced with the integer position of
    that value in column_names
    """
    try:
        # Dictionary of modifiers
        modifiers = dict((k, modifier_as_function(v)) for k, v in modifiers.items())
        if not column_names:
            return modifiers
        p2 = {}
        for k in modifiers:
            if k in column_names:
                idx = column_names.index(k)
                if idx in modifiers:
                    raise ColumnIdentifierError("Column %s has index %i which already has a pattern." % (k, idx))
                p2[idx] = modifiers[k]
            else:
                p2[k] = modifiers[k]
        return p2
    except AttributeError:
        # Sequence of modifiers
        return dict((idx, modifier_as_function(x)) for idx, x in enumerate(modifiers.values()))

def modifier_as_function(modifier):
    """
    Given a modifier (string or callable), return a callable modifier. If the modifier is a string, return the
    appropriate callable modifier by examinating the modifier type (first character).
    """
    # modifier is a callable modifier
    if hasattr(modifier, '__call__'):
        callable_modifier = modifier

    # modifier is a string modifier
    else:
        supported_modifier_types = ['s', 'y', 'e']
        if not modifier:
            raise InvalidModifier('empty modifier')
        modifier_type = modifier[0]
        if modifier_type not in supported_modifier_types:
            raise InvalidModifier('unsupported type `%s` in modifier `%s`; supported modifier types are %s' % (modifier_type, modifier, ', '.join(supported_modifier_types)))
        # perform dispatch
        callable_modifier = eval('%sModifier' % modifier_type.upper())(modifier)

    return callable_modifier

class Modifier(object):
    """
    Abstract modifier class, from which all modifier classes shall inherit. Perform common checks on the supplied modifier,
    to ease the subsequent operations in subclasses.
    """
    def __init__(self, modifier):
        if len(modifier) < 4:
            raise InvalidModifier('modifier is too short: `%s`' % modifier)

        modifier_type = modifier[0]

        ref_modifier_type = self.modifier_form[0] if len(self.modifier_form) > 0 else None
        if modifier_type != ref_modifier_type:
            raise InvalidModifier('expected type `%s`, got `%s` in `%s`' % (ref_modifier_type, modifier_type, modifier))

        modifier_sep = modifier[1]
        modifier_parts = modifier.split(modifier_sep)
        if len(modifier_parts) != 4:
            modifier_form = self.modifier_form.replace('/', modifier_sep)
            raise InvalidModifier('expected modifier of the form `%s`, got `%s`' % (modifier_form, modifier))

        modifier_lhs = modifier_parts[1]
        if not modifier_lhs:
            raise InvalidModifier('%s: no previous regular expression' % modifier)
        self.modifier_lhs = modifier_lhs

        modifier_rhs = modifier_parts[2]
        self.modifier_rhs = modifier_rhs

        flags = modifier_parts[3]
        for flag in flags:
            if flag not in self.supported_flags:
                message = 'invalid flag `%s` in `%s`' % (flag, modifier)
                if len(self.supported_flags) == 0:
                    message += '; no flag is supported for type `%s`' % modifier_type
                if len(self.supported_flags) == 1:
                    message += '; the only supported flag for type `%s` is %s' % (modifier_type, self.supported_flags[0])
                if len(self.supported_flags) > 1:
                    message += '; supported flags for type `%s` are %s' % (modifier_type, ', '.join(self.supported_flags))
                raise InvalidModifier(message)
        self.modifier_flags = flags

class SModifier(Modifier):
    """
    The "substitution" modifier ("s/REGEX/REPL/FLAGS").

    Replaces regular expression `REGEX` with replacement string
    `REPL`, which can use back references. Supports the following
    flags:

    * i: case-insensitive
    * g: global replacement (otherwise only the first is replaced)
    * l: uses locale-dependent character classes
    * m: enables multiline matching for "^" and "$"
    * s: "." also matches the newline character
    * u: enables unicode escape sequences
    * x: `REGEX` uses verbose descriptors & comments

    Note that the "/" character can be any character as long as it
      is used consistently and not used within the modifier,
      e.g. ``s|a|b|`` is equivalent to ``s/a/b/``.
    """
    def __init__(self, modifier):
        self.modifier_form = 's/REGEX/REPL/FLAGS'
        self.supported_flags = ['i', 'g', 'l', 'm', 's', 'u', 'x']

        super(SModifier, self).__init__(modifier)

        self.repl = self.modifier_rhs

        re_flags = 0
        for flag in self.modifier_flags:
            re_flags |= getattr(re, flag.upper(), 0)

        try:
            self.regex = re.compile(self.modifier_lhs, re_flags)
        except re.error as e:
            raise InvalidModifier('%s in `%s`' % (e.message, modifier))

        self.count = 0 if 'g' in self.modifier_flags else 1

    def __call__(self, value):
        return self.regex.sub(self.repl, value, count=self.count)

def cranges(pattern):
    """
    Given a pattern, expands it to a range of characters (crange).

    The dash character ("-") indicates a range
    of characters (e.g. "a-z" for all alphabetic characters).    If
    the dash is needed literally, then it must be the first or
    last character, or escaped with "\". The "\" character escapes
    itself. Only the "i" flag, indicating case-insensitive
    matching of `SRC`, is supported.

    Examples:
      [pattern]  ->  [crange]
      'a-f'      ->  'abcdef'
      'a\-f'     ->  'a-f'
      'abc-'     ->  'abc-'
      '-abc'     ->  '-abc')
      'a-c-e-g'  ->  'abcdefg'
    """
    ret = ''
    idx = 0
    while idx < len(pattern):
        c = pattern[idx]
        idx += 1
        if c == '-' and len(ret) > 0 and len(pattern) > idx:
            for i in range(ord(ret[-1]) + 1, ord(pattern[idx]) + 1):
                ret += chr(i)
            idx += 1
            continue
        if c == '\\' and len(pattern) > idx:
            c = pattern[idx]
            idx += 1
        ret += c
    return ret

class YModifier(Modifier):
    """
    The "transliterate" modifier ("y/SRC/DST/FLAGS").

    (This is a slightly modified version of sed's "y" command.)

    Each character in `SRC` is replaced with the corresponding character in `DST`.
    Character ranges are supported in SRC and DST for the "transliterate" modifier.

    Note that the "/" character can be any character as long as it
      is used consistently and not used within the modifier,
      e.g. ``s|a|b|`` is equivalent to ``s/a/b/``.
    """
    def __init__(self, modifier):
        self.modifier_form = 'y/SRC/DST/FLAGS'
        self.supported_flags = ['i']
        super(YModifier, self).__init__(modifier)

        src = cranges(self.modifier_lhs)
        dst = cranges(self.modifier_rhs)

        if len(src) != len(dst):
            raise InvalidModifier('expecting source and destination to have the same length, but %i != %i, got `%s`' % (src, dst, modifier))

        if 'i' in self.modifier_flags:
            src = src.lower() + src.upper()
            dst = 2 * dst

        self.table = {ord(src_char) : ord(dst_char) for src_char, dst_char in zip(src, dst)}

    def __call__(self, value):
        return value.translate(self.table)

class EModifier(Modifier):
    """
    The "execute" external program modifier ("s/REGEX/COMMAND/FLAGS").

      For cells matching `REGEX`, execute (using bash) the external
      command `COMMAND`, which can back-references to `REGEX`. All
      new lines are stripped in the output of `COMMAND`.

      The following flags are supported for `REGEX`:

      * i: case-insensitive
      * l: uses locale-dependent character classes
      * m: enables multiline matching for "^" and "$"
      * s: "." also matches the newline character
      * u: enables unicode escape sequences
      * x: `REGEX` uses verbose descriptors & comments

    Note that the "/" character can be any character as long as it
    is used consistently and not used within the modifier,
    e.g. ``s|a|b|`` is equivalent to ``s/a/b/``.
    """
    def __init__(self, modifier):
        self.modifier_form = 'e/REGEX/COMMAND/FLAGS'
        self.supported_flags = ['i', 'l', 'm', 's', 'u', 'x']
        super(EModifier, self).__init__(modifier)

        re_flags = 0
        for flag in self.modifier_flags:
            re_flags |= getattr(re, flag.upper(), 0)

        try:
            self.regex = re.compile(self.modifier_lhs, re_flags)
        except re.error as e:
            raise InvalidModifier('%s in `%s`' % (e.message, modifier))

        self.command = self.modifier_rhs

    def __call__(self, value):
        match = self.regex.match(value)
        if not match:
            return value

        command = match.expand(self.command)

        proc = subprocess.Popen(
            command, shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = proc.communicate(value.encode('utf-8'))
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        if proc.returncode != 0:
            sys.stderr.write('command `%s` failed: %s' % (command, err))
            sys.exit(1)

        out = out.replace('\n', '')
        return out