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

from functools import wraps
from wapi.formatters import get_formatter

class objname(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        func.obj_name = self.name
        return func

class extends(object):
    def __init__(self, extended):
        self.extended = extended

    def __call__(self, func):
        def new_func(*args, **kwargs):
            d = getattr(args[0].__class__, self.extended)(*args, **kwargs)
            d.update(func(*args, **kwargs))
            return d
        if hasattr(func, 'obj_name'):
            new_func.obj_name = func.obj_name
        return wraps(func)(new_func)

def include(obj, method=None, **kwargs):
    return serialization(obj, method, **kwargs)[1]

def include_list(objs, method=None, **kwargs):
    try:
        s = get_object_serialization(objs[0], method)
    except IndexError:
        return []
    return [s.method(obj, **kwargs) for obj in objs]

def chain(obj, method=None, **kwargs):
    return dict([serialization(obj, method, **kwargs)])

def proplist(obj, properties):
    return dict([(prop, getattr(obj, prop)) for prop in properties])

def merge(*args, **kwargs):
    """Merges any dictionaries passed as args with kwargs"""
    base = args[0]
    for arg in args[1:]:
        base.update(arg)

    base.update(kwargs)
    return base

def S(**kwargs):
    """Convenience function for creating dictionaries more cleanly"""
    return kwargs

def empty(obj_name):
    return { obj_name: {} }

_SERIALIZERS_REGISTRY = {}

class Serialization(object):
    def __init__(self, name, method):
        self.name = name
        self.method = method
    
    def apply(self, obj, **kwargs):
        return (self.name, self.method(obj, **kwargs))


class NoSerializationMethod(RuntimeError):
    pass

class BaseSerializerType(type):
    def __init__(mcs, name, bases, dct):
        super(BaseSerializerType, mcs).__init__(name, bases, dct)
        if getattr(mcs, 'serializes', None):
            _SERIALIZERS_REGISTRY[mcs.serializes] = mcs()
            
class BaseSerializer(object):
    obj_names = {}
    def __init__(self, *args, **kwargs):
        super(BaseSerializer, self).__init__(*args, **kwargs)
        for k, v in self.__class__.__dict__.iteritems():
            if hasattr(v, 'obj_name'):
                self.__class__.obj_names[v] = v.obj_name

    def obj_name(self, func):
        return self.__class__.obj_names.get(func)

    def default(self, obj, **kw):
        try:
            return dict([(k, v) for k, v in obj.__dict__.iteritems() if not k.startswith('_')])
        except AttributeError:
            return dict()

    def _get_serialization(self, obj, method):
        try:
            m = getattr(self, method or 'default')
        except AttributeError:
            raise NoSerializationMethod('Serialization "%s" is not defined in serializer "%s" for object "%s"' % \
                (method, _SERIALIZERS_REGISTRY.get(obj.__class__, Serializer).__name__, obj.__class__.__name__))
        return Serialization(self.obj_name(m) or obj.__class__.__name__.lower(), m)

    def _do_serialization(self, obj, method=None, **kw):
        serialization = self._get_serialization(obj, method)
        return serialization.apply(obj, **kw)

class Serializer(BaseSerializer):
    __metaclass__ = BaseSerializerType

class DictSerializer(Serializer):
    serializes = {}.__class__

    def default(self, obj, **kwargs):
        return dict([(k, chain(v)) for k, v in obj.iteritems()])

_DEFAULT_SERIALIZER = Serializer()

def get_class_serializer(cls):
    try:
        return _SERIALIZERS_REGISTRY[cls]
    except KeyError:
        return _DEFAULT_SERIALIZER

def get_object_serialization(obj, method=None):
    ser = get_class_serializer(obj.__class__)
    return ser._get_serialization(obj, method)

def serialize(format, objs, method=None, out=None, **kwargs):
    fmt = get_formatter(format)(out=out)
    fmt.start()

    if len(objs) == 0:
        fmt.empty()
    else:
        fmt.format_list([get_object_serialization(objs, method).apply(obj, **kwargs) for obj in objs])
    fmt.end()
    return fmt.get()

def serialize_one(format, obj, method, out=None, **kwargs):
    fmt = get_formatter(format)(out=out)
    fmt.start()
    serialization = get_object_serialization(obj, method)
    fmt.format(serialization.apply(obj, **kwargs))
    fmt.end()
    return fmt.get()

def serialization(obj, method=None, **kwargs):
    return get_object_serialization(obj, method).apply(obj, **kwargs)

