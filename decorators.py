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

"""Decorators which can be applied to Wapi functions. For convenience,
some of them share names with their counterparts in Django, altough they
can't be exchanged"""

import functools
from wapi.exceptions import ApiLoginRequired
from wapi.parameters import FunctionParameter

def wraps(wrapped, wrapper):
    """Contionally copies all the attributes a Wapi function can define"""
    assigned = ('__module__', '__name__', '__doc__')
    conditionally_assigned = ('_required_parameters_',
        '_optional_parameters_',
        '_read_only_',
        '_write_only_',
        '_private_',
    )

    for attr in conditionally_assigned:
        if hasattr(wrapped, attr):
            assigned += (attr, )

    return functools.wraps(wrapped, assigned=assigned)(wrapper)

def login_required(func):
    """Requires the API function to be called by a logged-in user"""
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise ApiLoginRequired
        return func(self, request, *args, **kwargs)

    wrapper.requires_login = True
    return wraps(func, wrapper)

def private(func):
    """Prevents an API function from being exposed"""
    func._private_ = True
    return func

def readonly(func):
    """Marks an API function as read-only"""
    func._read_only_ = True
    return func

def writeonly(func):
    """Marks an API function as write-only"""
    func._write_only_ = True
    return func

def undocumented(func):
    """Prevents an API function from being documented"""
    func._undocumented_ = True
    return func

class function_parameter(object):
    """Base class for decorators which specify function parameters"""
    func_attr = None
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_args(self, params, *args, **kwargs):
        """Walks trough the arguments, identifying their types and creating
        FunctionParameters as needed"""
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            params = self.add_args(params, *(args[0]))
            return params

        if isinstance(args[0], FunctionParameter):
            params.append(args[0])
            if len(args) > 1:
                params = self.add_args(params, *args[1:], **kwargs)
            return params

        params.append(FunctionParameter(*args, **kwargs))
        return params

    def __call__(self, func):
        params = getattr(func, self.__class__.func_attr, [])
        params = self.add_args(params, *self.args, **self.kwargs)
        setattr(func, self.__class__.func_attr, params)
        return func

class required_parameter(function_parameter):
    """Adds a required parameter to the target function"""
    func_attr = '_required_parameters_'

class optional_parameter(function_parameter):
    """Adds an optional parameter to the target function"""
    func_attr = '_optional_parameters_'

