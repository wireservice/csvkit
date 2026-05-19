"""
This module contains the global configuration for agate. Users should use
:meth:`get_option` and :meth:`set_option` to modify the global
configuration.

**Available configuation options:**

+-------------------------+------------------------------------------+-----------------------------------------+
| Option                  | Description                              | Default value                           |
+=========================+==========================================+=========================================+
| default_locale          | Default locale for number formatting     | default_locale('LC_NUMERIC') or 'en_US' |
+-------------------------+------------------------------------------+-----------------------------------------+
| horizontal_line_char    | Character to render for horizontal lines | '-'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+
| vertical_line_char      | Character to render for vertical lines   | '|'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+
| bar_char                | Character to render for bar chart units  | '░'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+
| printable_bar_char      | Printable character for bar chart units  | ':'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+
| zero_line_char          | Character to render for zero line units  | '▓'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+
| printable_zero_line_char| Printable character for zero line units  | '|'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+
| tick_char               | Character to render for axis ticks       | '+'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+
| ellipsis_chars          | Characters to render for ellipsis        | '...'                                   |
+-------------------------+------------------------------------------+-----------------------------------------+
| text_truncation_chars   | Characters for truncated text values     | '...'                                   |
+-------------------------+------------------------------------------+-----------------------------------------+
| number_truncation_chars | Characters for truncated number values   | '…'                                     |
+-------------------------+------------------------------------------+-----------------------------------------+

"""

from babel.core import default_locale

_options = {
    #: Default locale for number formatting
    'default_locale': default_locale('LC_NUMERIC') or 'en_US',
    #: Character to render for horizontal lines
    'horizontal_line_char': '-',
    #: Character to render for vertical lines
    'vertical_line_char': '|',
    #: Character to render for bar chart units
    'bar_char': '░',
    #: Printable character to render for bar chart units
    'printable_bar_char': ':',
    #: Character to render for zero line units
    'zero_line_char': '▓',
    #: Printable character to render for zero line units
    'printable_zero_line_char': '|',
    #: Character to render for axis ticks
    'tick_char': '+',
    #: Characters to render for ellipsis
    'ellipsis_chars': '...',
    #: Characters for truncated text values
    'text_truncation_chars': '...',
    #: Characters for truncated number values
    'number_truncation_chars': '…',
}


def get_option(key):
    """
    Get a global configuration option for agate.

    :param key:
        The name of the configuration option.
    """
    return _options[key]


def set_option(key, value):
    """
    Set a global configuration option for agate.

    :param key:
        The name of the configuration option.
    :param value:
        The new value to set for the configuration option.
    """
    _options[key] = value


def set_options(options):
    """
    Set a dictionary of options simultaneously.

    :param hash:
        A dictionary of option names and values.
    """
    _options.update(options)
