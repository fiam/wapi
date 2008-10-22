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

"""Some utility functions used by Wapi"""

from inspect import isclass

def is_api_function(func):
    """Returns True if the passed function is a an API function"""
    return hasattr(func, 'func_name') and \
        not func.func_name.startswith('_') and \
        not getattr(func, '_private_', False)

def api_iterate(obj):
    """Iterator over the API functions defined in a class"""
    for key in dir(obj):
        value = getattr(obj, key)
        if is_api_function(value):
            yield value

def get_instance(obj_or_cls):
    """Given a class or an instance, always return an instance"""
    if isclass(obj_or_cls):
        return obj_or_cls()

    if hasattr(obj_or_cls, '__iter__'):
        return [get_instance(o) for o in obj_or_cls]

    return obj_or_cls
