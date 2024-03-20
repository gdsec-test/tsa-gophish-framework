#!/bin/bash

set -eu

# Calculate the SHA1 hash of the scripts
SHA1HASH=$(cat *.py | shasum | cut -d' ' -f1)

# See if we can reuse the existing build
if [[ -f function.zip && -f lambda.sha1 && "$(< lambda.sha1)" == "${SHA1HASH}" ]]; then  
    echo "Reusing existing build"
    exit 0
fi

rm -f function.zip

zip -9 function.zip *.py

rm -rf package
mkdir package
pushd package
pip install -r ../requirements.txt --target .
zip -9rg ../function.zip .
popd
rm -rf package

# Store the SHA1 hash of the scripts
echo ${SHA1HASH} > lambda.sha1

# If S3 bucket parameters were specified, upload the resulting ZIP file
###  if [[ -n "$1" && -n "$2" ]]; then
if [[ $# == 2 ]]; then
    CODE_BUCKET="$1"
    LAMBDA="$2"

    # Upload the ZIP file to S3
    echo "Uploading ZIP file to S3"
    aws s3 cp function.zip s3://${CODE_BUCKET}/${LAMBDA}/${SHA1HASH}
fi
