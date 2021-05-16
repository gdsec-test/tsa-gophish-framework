"""\
Creates or modify the secretsmanager entry "GophishAPI" used by
the status lambda.  The entry contains connection information for the Gophish
API, and the status lambda uses this when retrieving campaign summary
information.
"""

import json
import logging

import botocore
import boto3
import pymysql.cursors

log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)


def handler(event, context):
    """Default lambda handler"""

    try:
        ssm_client = boto3.client("ssm", region_name="us-west-2")
        secretsmanager_client = boto3.client("secretsmanager", region_name="us-west-2")

        db_endpoint = ssm_client.get_parameter(Name="/Team/Aurora/gophish/Address")[
            "Parameter"
        ]["Value"]

        db_user_creds = json.loads(
            secretsmanager_client.get_secret_value(SecretId="GophishDBUserCredentials")[
                "SecretString"
            ]
        )

        connection = pymysql.connect(
            host=db_endpoint,
            user=db_user_creds["username"],
            password=db_user_creds["password"],
            database="gophish",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT `api_key` FROM `users` WHERE `username` = 'admin'"
                )
                api_key = cursor.fetchone()["api_key"]

        api_url = ssm_client.get_parameter(Name="/Gophish/API/Url")["Parameter"][
            "Value"
        ]

        try:
            secretsmanager_client.create_secret(
                Name="GophishAPI",
                Description="Gophish API configuration",
                SecretString=json.dumps({"api_key": api_key, "api_url": api_url}),
            )

        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ResourceExistsException":
                secretsmanager_client.put_secret_value(
                    SecretId="GophishAPI",
                    SecretString=json.dumps({"api_key": api_key, "api_url": api_url}),
                )

        log.info("postconfig executed successfully")

    except Exception:
        log.exception("postconfig failed")
