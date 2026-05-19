"""
Helpers for working with SVG.
"""

import xml.etree.ElementTree as ET

HEADER = '<?xml version="1.0" standalone="no"?>\n' + \
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n' + \
    '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'


def stringify(root):
    """
    Convert an SVG XML tree to a unicode string.
    """
    return ET.tostring(root, encoding='unicode')


def save(f, root):
    """
    Save an SVG XML tree to a file.
    """
    f.write(HEADER)
    f.write(stringify(root))


def translate(x, y):
    """
    Generate an SVG transform statement representing a simple translation.
    """
    return 'translate(%i %i)' % (x, y)


def rotate(deg, x, y):
    """
    Generate an SVG transform statement representing rotation around a given
    point.
    """
    return 'rotate(%i %i %i)' % (deg, x, y)
