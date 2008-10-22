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

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from wapi.auth.base import ApiAuth
from bynotes.digest.models import Challenge, Cnonce

import hashlib

def split_into_dict(value, sep=','):
    dct = {}
    for item in [v.strip () for v in value.split(sep)]:
        key, value = item.split('=', 1)
        dct[key] = value.strip('"')
    return dct

class ApiAuthDigest(ApiAuth):
    realm = ''
    def get_HA1(self, request, realm, user):
        """This should return hashlib.md5(username:realm:password).hexdigest()"""
        raise NotImplementedError

    def login(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            meth, auth = request.META['HTTP_AUTHORIZATION'].strip().split(' ', 1)
            if meth.lower() == 'digest':
                params = split_into_dict(auth)
                if self.__class__.realm != params.get('realm'):
                    return self.login_required(request)

                if request.get_full_path() != params.get('uri'):
                    return self.login_required(request)

                try:
                    challenge = Challenge.objects.get(opaque=params['opaque'])
                    user = User.objects.get(username=params['username'])
                except (KeyError, Challenge.DoesNotExist, User.DoesNotExist):
                    return self.login_required(request)

                if challenge.nonce != params.get('nonce'):
                    return self.login_required(request)

                if not challenge.validate_nc(params.get('nc')):
                    return self.login_required(request)

                ha1 = self.get_HA1(request, self.__class__.realm, user)
                ha2 = hashlib.md5('%s:%s' % (request.method, request.get_full_path())).hexdigest()
                ha = hashlib.md5('%s:%s:%s:%s:%s:%s' % (ha1, challenge.nonce,
                    params.get('nc'), params.get('cnonce'), 'auth', ha2)).hexdigest()

                if ha != params.get('response'):
                    return self.login_required(request)

                cnonce, cr = Cnonce.objects.get_or_create(challenge=challenge, cnonce=params.get('cnonce'))
                if not cr:
                    return self.stale(request, challenge)

                request.user = user

        return None

    def stale(self, request, challenge):
        """Returned when the cnonce has been used"""
        response = HttpResponse(_('Authorization Required'), mimetype='text/plain')
        response['WWW-Authenticate'] = 'Digest realm="%s",qop="auth",nonce="%s",opaque="%s",stale="true"' % \
            (self.__class__.realm, challenge.nonce, challenge.opaque)

        response.status_code = 401
        return response

    def login_required(self, request):
        """Return a response with the params the client needs to perform
        digest authentication"""

        challenge = Challenge.objects.create()
        response = HttpResponse(_('Authorization Required'), mimetype='text/plain')
        response['WWW-Authenticate'] = 'Digest realm="%s",qop="auth",nonce="%s",opaque="%s"' % \
            (self.__class__.realm, challenge.nonce, challenge.opaque)

        response.status_code = 401
        return response

