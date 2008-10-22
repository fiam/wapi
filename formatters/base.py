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

"""Metaclass and abstract class for all the formatters"""

_FORMATTERS_REGISTER = {}

class FormatterType(type):
    """Metaclass for formatters. Autoregisters them"""
    def __init__(mcs, name, bases, dct):
        if getattr(mcs, 'format_name', None) and \
            not mcs.format_name in _FORMATTERS_REGISTER:
            _FORMATTERS_REGISTER[mcs.format_name] = mcs
        super(FormatterType, mcs).__init__(name, bases, dct)

class BaseFormatter(object):
    """Abstract base class for all the formatters"""
    def __init__(self, *args, **kwargs):
        self.data = ''
        self.out = kwargs.get('out')

    def start(self):
        """Called before a new formatting starts"""
        pass

    def end(self):
        """Called after the formatting ends and before retrieving the result"""
        pass

    def empty(self):
        """Called when an empty formatting is requested"""
        pass

    def get(self):
        """Retrieves the result of the formatting"""
        if self.out:
            self.out.write(self.data)
            return self.out

        return self.data

    def format_list(self, data):
        """Formats a list of elements"""
        raise NotImplementedError

    def format(self, data):
        """Formats a single element"""
        raise NotImplementedError

class Formatter(BaseFormatter):
    __metaclass__ = FormatterType

