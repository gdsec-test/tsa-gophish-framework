#!/bin/bash
aws lambda update-function-code --function-name preconfig --zip-file fileb://function.zip
