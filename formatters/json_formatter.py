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

"""simplejson based JSON encoder"""

from decimal import Decimal
from datetime import datetime

try:
    from django.utils import simplejson
except ImportError:
    import simplejson

from django.utils.encoding import smart_unicode
from wapi.formatters.base import Formatter

class JsonEncoder(simplejson.JSONEncoder):
    """Extends the default encoder, using the class __unicode__ to
    represent unknown objects"""
    def default(self, obj):
        try:
            return simplejson.JSONEncoder.default(self, obj)
        except TypeError:
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, datetime):
                return obj.strftime('%a, %d %b %Y %H:%M:%S %z')
            return smart_unicode(obj)

class JsonFormatter(Formatter):
    format_name = 'json'

    def format(self, data):
        self.data = simplejson.dumps(data[1], cls=JsonEncoder)

    def format_list(self, data):
        self.data = simplejson.dumps([obj[1] for obj in data], cls=JsonEncoder)

    def empty(self):
        self.data = '[]'

