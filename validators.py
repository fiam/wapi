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

import re

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy, ugettext as _

ALPHA_NUMERIC_RE = re.compile('\w+')

class Validator(object):
    """Base class for all the Wapi validators"""
    DOC_NAMES = {}
    def validate(self, value):
        """Validates the given value, raising ValidationError if appropiate"""
        raise ValidationError

    def __call__(self, value):
        """Triggers the validation"""
        return self.validate(value)

    def doc_info(self):
        """Returns documentation information for this validator"""
        return [(v, getattr(self, k)) for k, v in self.DOC_NAMES.iteritems() \
            if getattr(self, k, None) is not None]


class BoolValidator(Validator):
    """Validates that the given value is a boolean"""
    def validate(self, value):
        """Accepts t, 1 and true as True and f, 0 and false as False"""
        if value.lower() in ('t', 'true', '1'):
            return True
        if value.lower() in ('f', 'false', '0'):
            return False

        raise ValidationError(_('Not a boolean'))


class IntegerValidator(Validator):
    """Validates that the given value can be converted to an integer"""
    def validate(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(_('Not an integer'))


class FloatValidator(Validator):
    """Validates that the given value can be converted to a float"""
    def validate(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(_('Not a float'))


class StringValidator(Validator):
    """Validates that the given value is a string with its length between
        the specified range (if any)"""
    DOC_NAMES = {
        'max_length': ugettext_lazy('Maximum length'),
        'min_length': ugettext_lazy('Minimum length'),
    }
    def __init__(self, *args, **kwargs):
        super(StringValidator, self).__init__(*args, **kwargs)
        self.max_length = kwargs.get('max_length')
        self.min_length = kwargs.get('min_length')

    def validate(self, value):
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(_('This value is too long ' \
                '(max is %d chars)') % self.max_length)

        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(_('This value is too short ' \
                '(min is %d chars)') % self.max_length)

        return value

class UnicodeValidator(StringValidator):
    """Validates that the given value is an unicode string or can be converted
        to unicode and its length is between the specified range (if any)"""
    def validate(self, value):
        if not isinstance(value, unicode):
            try:
                value = unicode(value, 'utf8')
            except UnicodeError:
                raise ValidationError, _('Invalid unicode')

        return super(UnicodeValidator, self).validate(value)

class AlphaNumericValidator(Validator):
    """Validates that the given value is an alphanumeric string"""
    def validate(self, value):
        import re
        alnum_re = re.compile(r'^\w+$')
        if not alnum_re.search(value):
            raise ValidationError, _("This value must contain only letters, numbers and underscores.")
        return value


class RangeValidator(Validator):
    """Validates that the given value is between the given range"""
    DOC_NAMES = {
        'max_value': ugettext_lazy('Maximum value'),
        'min_value': ugettext_lazy('Minimum value'),
    }
    def __init__(self, *args, **kwargs):
        super(RangeValidator, self).__init__(args, kwargs)
        self.min_value = kwargs.get('min_value')
        self.max_value = kwargs.get('max_value')

    def validate(self, value):
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(_('This value is less than the min (%s)') \
                % self.min_value)

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(_('This value is greater than the max (%s)')\
                 % self.max_value)

        return value


class CommaSeparatedIntegersValidator(Validator):
    """Validates that the given value is a comma-separated list of integers"""
    def __init__(self, *args, **kwargs):
        super(CommaSeparatedIntegersValidator, self).__init__(*args, **kwargs)
        self.keep = kwargs.get('keep', False)
        self.integer_validator = IntegerValidator()

    def validate(self, value):
        values = []
        for val in value.split(','):
            values.append(self.integer_validator.validate(val))

        if self.keep:
            return value

        return values


class ChoiceValidator(Validator):
    """Validates that the given value is one of the provided choices"""
    def __init__(self, *args, **kwargs):
        super(ChoiceValidator, self).__init__(*args, **kwargs)
        self.choices = kwargs.get('choices')
        self.toupper = kwargs.get('toupper', False)
        self.tolower = kwargs.get('tolower', False)
        self.valid_choices = set()
        for choice in self.choices:
            if not isinstance(choice, tuple) or len(choice) != 2:
                raise RuntimeError('Choices should be an iterable with ' \
                    'tuples of size 2')
            self.valid_choices.add(choice[0])

    def validate(self, value):
        if self.tolower:
            value = value.lower()
        if self.toupper:
            value = value.upper()

        if not value in self.valid_choices:
            raise ValidationError, _('"%s" is not a valid choice') % value

        return value

    def doc_info(self):
        """Return the available choices"""
        return [(_('Valid choices'),
            ', '.join(['%s (%s)' % (v1, _(v2)) for v1, v2 in self.choices]))]

class FileSizeValidator(Validator):
    """Validates that the given file is between the provided range"""
    DOC_NAMES = {
        'max_size': _('Maximum file size'),
        'min_size': _('Minimum file size'),
    }
    def __init__(self, *args, **kwargs):
        super(FileSizeValidator, self).__init__(*args, **kwargs)
        self.max_size_bytes = None
        self.min_size_bytes = None
        self.max_size = kwargs.get('max_size')
        self.min_size = kwargs.get('min_size')
        for attr in ('max_size', 'min_size'):
            value = getattr(self, attr)
            if isinstance(value, basestring):
                for i, suffix in enumerate(('K', 'M', 'G')):
                    if  attr.endswith(suffix):
                        setattr(self, '%s_bytes' % attr,
                            int(self.max_size[:-1]) * (1024 ** (i + 1)))
                        break
            else:
                setattr(self, '%s_bytes' % attr, value)

    def validate(self, value):
        if self.max_size_bytes is not None and value.size > self.max_size_bytes:
            raise ValidationError(_('This file is too big (max %s)') % \
                self.max_size)

        if self.min_size_bytes is not None and value.size < self.min_size_bytes:
            raise ValidationError(_('This file is too small (min %s)') % \
                self.min_size)

        return value

TYPE_VALIDATORS = {
    bool: BoolValidator,
    int: IntegerValidator,
    float: FloatValidator,
    str: StringValidator,
    basestring: StringValidator,
    unicode: UnicodeValidator,
    file: None,
}

def validate_type(value_type, value):
    """Validates a value given its type"""
    try:
        return TYPE_VALIDATORS[value_type](value)
    except KeyError:
        return value

def get_type_validator(value_type):
    """Returns the validator for the given type"""
    try:
        return TYPE_VALIDATORS[value_type]
    except KeyError:
        return None

