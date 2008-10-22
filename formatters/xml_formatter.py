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

"""cElementTree base XML formatter"""

from datetime import datetime

from django.utils.encoding import smart_unicode
from wapi.formatters.base import Formatter

from xml.etree import cElementTree as ET

class XmlFormatter(Formatter):
    format_name = 'xml'

    def __init__(self, *args, **kwargs):
        super(XmlFormatter, self).__init__(*args, **kwargs)
        self.root = None

    def start(self, name='objects'):
        self.root = ET.Element(name)

    def end(self):
        self.data = ET.tostring(self.root, 'utf8')

    def format_element(self, parent, data):
        """Formats one element and appends it to 'parent'"""
        for key, value in data.items():
            element = ET.SubElement(parent, key)
            if isinstance(value, dict):
                self.format_element(element, value)
            elif isinstance(value, list) or isinstance(value, tuple):
                for item in value:
                    self.format_element(element, { 'item': item })
            elif isinstance(value, datetime):
                element.text = value.strftime('%a, %d %b %Y %H:%M:%S %z')
            else:
                element.text = smart_unicode(value)

    def format_list(self, data):
        for obj in data:
            self.format_element(self.root, {obj[0]: obj[1]})

    def format(self, obj):
        self.start(obj[0])
        self.format_element(self.root, obj[1])

