#!/bin/bash
aws lambda update-function-code --function-name postconfig --zip-file fileb://function.zip
