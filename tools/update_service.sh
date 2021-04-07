#!/bin/bash
aws ecs update-service --cluster PhishFramework --service gophish --force-new-deployment
aws ecs update-service --cluster PhishFramework --service landing --force-new-deployment
