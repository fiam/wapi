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

"""ApiDocumentator: documents your API"""

from django.views.generic.simple import direct_to_template

from wapi.function import ApiFunction, ApiNamespace
from wapi.utils import api_iterate, get_instance

class ApiDocumentator(object):
    """This class acts as a view which documents the given API. Optionally
    accepts a list of supported authentication methods."""
    def __init__(self, api, auth_methods=None):
        self.auth_methods = get_instance(auth_methods or [])
        self.api = get_instance(api)

    def __call__(self, request):
        functions = []
# This does not work for now
#        auth_docs = []
#        for auth in self.auth_methods:
#            auth_docs.append((auth.doc_name, auth.get_docs()))
        for func in api_iterate(self.api):
            function = ApiFunction(func)
            if function.documented:
                functions.append(function)

        functions.sort(cmp=lambda x, y: cmp(x.name, y.name))
        if hasattr(self.api.__class__, 'NAMESPACES'):
            namespaces = []
            for name, nsname in self.api.NAMESPACES:
                namespaces.append(ApiNamespace(name, nsname, functions))

        return direct_to_template(request, 'wapi/documentation.html',
            {
                'functions': functions,
                'namespaces': namespaces,
            }
        )
