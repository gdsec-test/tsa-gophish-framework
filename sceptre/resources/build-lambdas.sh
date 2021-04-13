#!/bin/bash

# This script supports the build process for lambda resources:
# - Store a SHA1 hash of each lambda source so the CloudFormation templates can
#   use it to detect differences and trigger an update
# - Create a ZIP file with the required python modules and upload it to S3 so
#   that the CloudFormation template can reference it

set -eu

PHISH_FRAMEWORK_SOURCE=$(cd `dirname $0`/../.. && pwd)

CODE_BUCKET=$(aws s3api list-buckets --output text --query 'Buckets[?ends_with(Name, `code-bucket`)].Name')
LAMBDAS=$(ls ${PHISH_FRAMEWORK_SOURCE}/lambdas)

for LAMBDA in ${LAMBDAS}
do
    echo Building ${LAMBDA} lambda

    pushd ${PHISH_FRAMEWORK_SOURCE}/lambdas/${LAMBDA}

    if [ -x "build.sh" ]; then
        # Build and upload the lambda using the supplied build script
        ./build.sh ${CODE_BUCKET} ${LAMBDA}
    fi

    popd

done
