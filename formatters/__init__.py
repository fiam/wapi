# -*- coding: utf-8 -*-

# Copyright (c) 2008 Alberto García Hierro <fiam@rm-fr.net>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Formatters for outputing serialized objects in Wapi"""

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# Import as many formatters as possible
try:
    from wapi.formatters.json_formatter import JsonFormatter
except ImportError:
    pass

try:
    from wapi.formatters.xml_formatter import XmlFormatter
except ImportError:
    pass

try:
    from wapi.formatters.yaml_formatter import YamlFormatter
except ImportError:
    pass

from wapi.formatters.base import _FORMATTERS_REGISTER

class UnknownFormat(Exception):
    """Raised when the formatter for an unknown format is requested"""
    pass

def get_formatter(format):
    """Returns the formatter for the given format"""
    try:
        return _FORMATTERS_REGISTER[format]
    except KeyError:
        raise RuntimeError('No formatter registered for format "%s"' % format)

def register_formatter(cls):
    if getattr(cls, 'format_name'):
        _FORMATTERS_REGISTER[cls.format_name] = cls
    else:
        raise RuntimeError('Class %s is not a valid formatter')

