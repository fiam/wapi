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

"""HTTP $esponses which format object in different formats"""

from django.http import HttpResponse
from wapi.serializers import serialize, serialize_one
from wapi.formatters import UnknownFormat

_RESPONSES_REGISTRY = {}

def get_response(format):
    """Given a format, returns its correspondant response class"""
    try:
        return _RESPONSES_REGISTRY[format]
    except KeyError:
        raise UnknownFormat

class SerializableResponse(object):
    """A special class which can be converted to a SerializedResponse"""
    def __init__(self, objs, method=None, *args, **kwargs):
        self.objs = objs
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def transform(self, cls):
        """Do the actual conversion to the passed class"""
        return cls(self.objs, self.method, *self.args, **self.kwargs)

class SingleSerializableResponse(SerializableResponse):
    """SerializableResponse which works on non-iterable objects"""
    def transform(self, cls):
        """Transform using serialize_one instead of serialize"""
        return cls(self.objs, self.method, serialize=serialize_one,
            *self.args, **self.kwargs)

class SerializedResponseType(type):
    """Metaclass for serialized responses, adds them to the registry"""
    def __init__(mcs, name, bases, dct):
        if hasattr(mcs, 'formatter') and mcs.formatter:
            _RESPONSES_REGISTRY[mcs.formatter] = mcs

        super(SerializedResponseType, mcs).__init__(name, bases, dct)

class SerializedResponse(HttpResponse):
    """Base class for all responses which return serialized objects"""
    __metaclass__ = SerializedResponseType
    content_type = None
    formatter = None
    def __init__(self, objs, method=None, *args, **kwargs):
        self.serialize = kwargs.pop('serialize', serialize)
        content = self.serialize(self.__class__.formatter,
            objs, method, *args, **kwargs)
        super(SerializedResponse, self).__init__(content,
            content_type=self.__class__.content_type)

class JsonResponse(SerializedResponse):
    """Returns objects formatted as JSON. Accepts a 'jscb' parameter, indicating
    the JSONP callback"""
    content_type = 'application/json'
    formatter = 'json'
    def __init__(self, objs, method=None, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(JsonResponse, self).__init__(objs, method, *args, **kwargs)
        if self.request and 'jscb' in self.request.REQUEST:
            self.content = '%s(%s)' % \
                (self.request.REQUEST['jscb'], self.content)

class XmlResponse(SerializedResponse):
    """Returns objects formatted as XML"""
    content_type = 'application/xml'
    formatter = 'xml'

class YamlResponse(SerializedResponse):
    """Returns objects formatted as YAML"""
    content_type = 'application/x-yaml'
    formatter = 'yaml'
