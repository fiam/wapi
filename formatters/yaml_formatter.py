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

"""PyYAML based YAML formatter"""

from decimal import Decimal
from datetime import datetime

import yaml
from wapi.formatters.base import Formatter

class Dumper(yaml.dumper.SafeDumper):
    """Dumper with support for representing Decimal objects,
    generators and datetime objects as per RFC2822"""
    def __init__(self, *args, **kwargs):
        super(Dumper, self).__init__(*args, **kwargs)

    def represent_decimal(self, value):
        """Represent Decimal as float"""
        return self.represent_scalar(u'tag:yaml.org,2002:float', str(value))

    def represent_datetime(self, value):
        """Represent datetime.datetime as per RFC2822"""
        return self.represent_unicode(value.strftime('%a, %d %b %Y %H:%M:%S %z'))

Dumper.add_representer(Decimal, Dumper.represent_decimal)
Dumper.add_representer(datetime, Dumper.represent_datetime)
Dumper.add_representer((x for x in []).__class__, Dumper.represent_list)

class YamlFormatter(Formatter):
    format_name = 'yaml'

    def format(self, data):
        self.data = yaml.dump({data[0]: data[1]}, Dumper=Dumper)

    def format_list(self, data):
        self.data = yaml.dump(({obj[0]: obj[1]} for obj in data), Dumper=Dumper)

