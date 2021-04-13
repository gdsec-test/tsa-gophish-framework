#!/bin/bash
aws lambda update-function-code --function-name status --zip-file fileb://function.zip
