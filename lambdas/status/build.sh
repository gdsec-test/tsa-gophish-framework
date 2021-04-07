#!/bin/bash

set -eu

rm -f function.zip

zip -9r function.zip index.py

rm -rf package
mkdir package
pushd package
pip install git+ssh://git@github.secureserver.net/auth-contrib/PyAuth.git@7.2.2#egg=PyAuth --target .
pip install gophish --target .
zip -9rg ../function.zip .
popd
rm -rf package

aws lambda update-function-code --function-name status --zip-file fileb://function.zip

rm -f function.zip
