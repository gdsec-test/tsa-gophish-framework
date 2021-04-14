#!/usr/bin/env python3

"""\
This script creates the gophish database and the user credentials to access it.
"""

import json

import boto3
import pymysql.cursors

ssm_client = boto3.client("ssm", region_name="us-west-2")
secretsmanager_client = boto3.client("secretsmanager", region_name="us-west-2")

DB_ENDPOINT = ssm_client.get_parameter(Name="/Team/Aurora/gophish/Address")[
    "Parameter"
]["Value"]

DB_ADMIN_CREDS = json.loads(
    secretsmanager_client.get_secret_value(SecretId="gophish")["SecretString"]
)

DB_USER_CREDS = json.loads(
    secretsmanager_client.get_secret_value(SecretId="GophishDBUserCredentials")[
        "SecretString"
    ]
)

connection = pymysql.connect(
    host=DB_ENDPOINT,
    user=DB_ADMIN_CREDS["username"],
    password=DB_ADMIN_CREDS["password"],
    database="mysql",
    cursorclass=pymysql.cursors.DictCursor,
)

with connection:
    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS `gophish` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(
            'CREATE USER IF NOT EXISTS "%s" IDENTIFIED BY "%s"'
            % (DB_USER_CREDS["username"], DB_USER_CREDS["password"])
        )
        cursor.execute("GRANT ALL ON gophish.* TO '%s'" % DB_USER_CREDS["username"])
        cursor.execute("FLUSH PRIVILEGES")
