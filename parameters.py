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

from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError

from wapi.validators import get_type_validator
from wapi.exceptions import ApiMissingParam, ApiInvalidParam

FRIENDLY_TYPE_NAMES = {
    int: _('Integer'),
    float: _('Floating point number'),
    basestring: _('String'),
    str: _('String'),
    unicode: _('UTF-8 String'),
    bool: _('Boolean'),
    file: _('File'),
}

class FunctionParameter(object):
    """Class encapsulating a function parameter with its validators"""
    def __init__(self, name, param_type, doc=None, validators=None,
            default=None):
        self.name = name
        self.param_type = param_type
        self.doc = doc
        self.validators = validators or []
        if self.validators and not hasattr(self.validators, '__iter__'):
            self.validators = [self.validators]
        
        validator = get_type_validator(param_type)
        if validator and validator.__class__ not in \
                [v.__class__ for v in self.validators]:
            self.validators = [validator()] + list(self.validators)
        self.default = default

    def get(self, request, dct):
        """Returns the value for this parameter in the given dictionary
        after validating it"""
        try:
            value = dct[self.name]
        except KeyError:
            raise ApiMissingParam(param=self.name)

        for validator in self.validators:
            try:
                value = validator(value)
            except ValidationError:
                raise ApiInvalidParam(param=self.name, value=value)

        dct[self.name] = value
        return value

    def set_default(self, request, dct):
        """Store the default value in the given dictionary"""
        dct[self.name] = self.default

    def has_default(self):
        """Wheter the parameter has a default value"""
        return self.default is not None

    @property
    def type_name(self):
        """Returns the friendly name for the parameter type"""
        try:
            return FRIENDLY_TYPE_NAMES[self.param_type]
        except KeyError:
            try:
                return self.param_type.__name__
            except AttributeError:
                return unicode(self.param_type)

    def doc_info(self):
        """Returns documentation derived from information from te validators"""
        info = []
        for validator in self.validators:
            info += validator.doc_info()

        return info

class FileFunctionParameter(FunctionParameter):
    """A special function parameter which represents an uploaded file"""
    def __init__(self, name, doc=None, validators=None):
        super(FileFunctionParameter, self).__init__(name, file, doc, validators)

    def set_default(self, request, dct):
        """Do nothing, since this validator can't provide a default"""
        pass

    def has_default(self):
        """No default possible"""
        return False

    def get(self, request, dct):
        """Get the file objects from request.FILES and validate it"""
        try:
            fobj = request.FILES[self.name]
        except KeyError:
            raise ApiMissingParam(param=self.name)

        for validator in self.validators:
            validator(fobj)

        dct[self.name] = fobj
        return fobj

class FunctionParameterSet(object):
    """Container for multiple FunctionParameters"""
    def __init__(self, *args):
        self.parameters = []
        for arg in args:
            if isinstance(arg, FunctionParameter):
                self.parameters.append(arg)
            else:
                self.parameters.append(FunctionParameter(*arg))

    def __getslice__(self, start, end):
        return self.parameters.__getslice__(start, end)

    def __iter__(self):
        return self.parameters.__iter__()


