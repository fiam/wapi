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

"""Exceptions that can be thrown from Wapi. Every one of them will
    generate a response matching the type of the exception."""

from django.http import HttpResponse

class ApiError(RuntimeError):
    """Generic API Error"""
    default_msg = 'API Error'
    status_code = 400

    def __init__(self, message=None):
        RuntimeError.__init__(self, message or self.__class__.default_msg)

    def get_message(self):
        """Returns the message contained in the response, some
        exceptions override it"""
        return self.message

    def get_response(self):
        """Returns an HttpResponse using the code defined in the class"""
        response = HttpResponse(self.get_message())
        response.status_code = self.__class__.status_code
        return response


class ApiLoginRequired(ApiError):
    """The requested action requires a valid user"""
    default_msg = 'Authentication required'
    status_code = 401


class ApiBadRequest(ApiError):
    """Bad parameters present in the request"""
    default_msg = 'Bad request'
    status_code = 400

class ApiMissingParam(ApiBadRequest):
    """A required parameter was omitted"""
    default_msg = 'Missing parameter'

    def __init__(self, message=None, param=None):
        ApiBadRequest.__init__(self, message)
        if param:
            self.message = 'Missing required parameter "%s"' % param

class ApiInvalidParam(ApiBadRequest):
    """A parameter had a bad value"""
    default_msg = 'Parameter with invalid value'

    def __init__(self, message=None, param=None, value=None):
        ApiBadRequest.__init__(self, message)
        if param and value:
            self.message = 'Value "%s" for parameter "%s" is not valid' % \
                (param, value)

class ApiForbidden(ApiError):
    """The user hasn't permission to perform the requested action"""
    status_code = 403
    default_msg = 'Permission denied'

class ApiEmpty(ApiError):
    """No data to return"""
    status_code = 200
    default_msg = ''
