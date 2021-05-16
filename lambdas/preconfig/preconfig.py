"""\
Create the gophish database and the user credentials to access it.
"""

import json
import logging

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

        db_admin_creds = json.loads(
            secretsmanager_client.get_secret_value(SecretId="gophish")["SecretString"]
        )

        db_user_creds = json.loads(
            secretsmanager_client.get_secret_value(SecretId="GophishDBUserCredentials")[
                "SecretString"
            ]
        )

        connection = pymysql.connect(
            host=db_endpoint,
            user=db_admin_creds["username"],
            password=db_admin_creds["password"],
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
                    % (db_user_creds["username"], db_user_creds["password"])
                )
                cursor.execute(
                    "GRANT ALL ON gophish.* TO '%s'" % db_user_creds["username"]
                )
                cursor.execute("FLUSH PRIVILEGES")

        log.info("preconfig executed successfully")

    except Exception:
        log.exception("preconfig failed")
