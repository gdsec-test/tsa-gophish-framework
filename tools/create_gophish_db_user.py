#!/usr/bin/env python3

import json
import boto3

ssm_client = boto3.client("ssm")

DB_ENDPOINT = ssm_client.get_parameter(Name="/Team/Aurora/gophish/Address")[
    "Parameter"
]["Value"]

secretsmanager_client = boto3.client("secretsmanager")

DB_ADMIN_CREDS = json.loads(
    secretsmanager_client.get_secret_value(SecretId="gophish")["SecretString"]
)

DB_USER_CREDS = json.loads(
    secretsmanager_client.get_secret_value(SecretId="GophishDBUserCredentials")[
        "SecretString"
    ]
)
