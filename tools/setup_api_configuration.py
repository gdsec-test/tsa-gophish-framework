#!/usr/bin/env python3

import json

import botocore
import boto3
import pymysql.cursors

ssm_client = boto3.client("ssm", region_name="us-west-2")
secretsmanager_client = boto3.client("secretsmanager", region_name="us-west-2")

DB_ENDPOINT = ssm_client.get_parameter(Name="/Team/Aurora/gophish/Address")[
    "Parameter"
]["Value"]

DB_USER_CREDS = json.loads(
    secretsmanager_client.get_secret_value(SecretId="GophishDBUserCredentials")[
        "SecretString"
    ]
)

connection = pymysql.connect(
    host=DB_ENDPOINT,
    user=DB_USER_CREDS["username"],
    password=DB_USER_CREDS["password"],
    database="gophish",
    cursorclass=pymysql.cursors.DictCursor,
)

with connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT `api_key` FROM `users` WHERE `username` = 'admin'")
        API_KEY = cursor.fetchone()["api_key"]

API_URL = ssm_client.get_parameter(Name="/Gophish/API/Url")["Parameter"]["Value"]

try:
    secretsmanager_client.create_secret(
        Name="GophishAPI",
        Description="Gophish API configuration",
        SecretString=json.dumps({"api_key": API_KEY, "api_url": API_URL}),
    )

except botocore.exceptions.ClientError as error:
    if error.response["Error"]["Code"] == "ResourceExistsException":
        secretsmanager_client.put_secret_value(
            SecretId="GophishAPI",
            SecretString=json.dumps({"api_key": API_KEY, "api_url": API_URL}),
        )
