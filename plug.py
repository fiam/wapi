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

### THIS IS CURRENTLY NOT WORKING ###

import re

from django.http import Http404

from wapi.documentator import ApiDocumentator
from wapi.utils import get_instance

class ApiPlug(object):
    version = '1.0'
    bindings = []
    auth_methods = []
    api = None

    def __init__(self, base, *args, **kwargs):
        super(ApiPlug, self).__init__(args, kwargs)
        cls = self.__class__
        self.documentator = ApiDocumentator(auth_methods=cls.auth_methods, api=cls.api)
        self.bnds = []
        self.re = {
            re.compile(r'/%s%s/doc/$' % (base, cls.version)): self.documentator.__call__,
        }
        if not cls.auth_methods:
            for binding in cls.bindings:
                bnds.append(binding())
                self.re.update({
                    re.compile(r'/%s%s/%s/$' % (base, cls.version, binding)): self.documentator.__call__,
                })

    def __call__(self, request):
        for r in self.re:
            if r.search(request.path):
                return self.re[r](request)

        raise Http404
