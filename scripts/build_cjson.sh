#!/bin/sh

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

set -e

PYCJSON_VERSION="1.0.3x6"
PYCJSON_NAME="python-cjson"
PYCJSON="${PYCJSON_NAME}-${PYCJSON_VERSION}"
PYCJSON_TGZ="${PYCJSON}.tar.gz"
PYCJSON_URL="http://abra.rm-fr.net/~fiam/code/3rdparty/${PYCJSON_NAME}/${PYCJSON_TGZ}"
PYCJSON_PATCH_URL="http://abra.rm-fr.net/~fiam/code/${PYCJSON}+datetime+decimal-warnings.patch"

if test `basename $PWD` != "wapi"; then
    echo "Run this script from the wapi root directory" 1>&2
fi

wget ${PYCJSON_URL}
tar xzf ${PYCJSON_TGZ}
rm -f ${PYCJSON_TGZ}
cd ${PYCJSON}
wget -O - ${PYCJSON_PATCH_URL}|patch -p1
python setup.py build
mv build/lib*/cjson.so ../
cd ..
rm -fr ${PYCJSON}
