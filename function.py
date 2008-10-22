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

"""Classes encapsulating Wapi functions into more abstracted containers"""

import re

from wapi.exceptions import ApiMissingParam

NAMESPACE_RE = re.compile('(.*)__.*?')

class ApiFunction(object):
    """Encapsulates a Wapi function"""
    def __init__(self, func):
        self.func = func
        self.name = func.func_name
        self.required_parameters = getattr(func, '_required_parameters_', [])
        self.optional_parameters = getattr(func, '_optional_parameters_', [])
        self.doc = func.__doc__

    def __call__(self, request, dct):
        for parameter in self.required_parameters:
            parameter.get(request, dct)
        for parameter in self.optional_parameters:
            try:
                parameter.get(request, dct)
            except ApiMissingParam:
                parameter.set_default(request, dct)

        return self.func(request, dct)


    @property
    def requires_login(self):
        """Wheter the function requires a logged-in user"""
        return hasattr(self.func, 'requires_login') and self.func.requires_login

    @property
    def endpoint(self):
        """Returns the function endpoint used by the RestBinding"""
        return self.name.replace('__', '/')

    @property
    def is_read(self):
        """Wheter the function can be called as a read function"""
        return not getattr(self.func, '_write_only', False)

    @property
    def is_write(self):
        """Wheter the function can be called as a write function"""
        return not getattr(self.func, '_read_only_', False)

    @property
    def documented(self):
        """Wheter the function should be documented"""
        return not getattr(self.func, '_undocumented_', False)

    def namespace(self):
        """Returns the namespace this function belongs to"""
        match = NAMESPACE_RE.match(self.name)
        if match:
            return match.group(1)

        return u''

class ApiNamespace(object):
    """Container grouping multiple functions into the same namespace"""
    def __init__(self, name, short_name, functions):
        self.name = name
        self.short_name = short_name
        self.functions = [f for f in functions if f.namespace() == short_name]
        self.functions.sort(cmp=lambda x, y: cmp(x.name, y.name))

    def __iter__(self):
        return self.functions.__iter__()

