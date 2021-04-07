#!/usr/bin/env python3

import json
import logging
import os

import boto3

log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)

logging_handler = logging.StreamHandler()
logging_formatter = logging.Formatter("[%(levelname)s] %(asctime)s %(message)s")
logging_handler.setFormatter(logging_formatter)
log.addHandler(logging_handler)

gophish_config = {
    "admin_server": {"listen_url": "0.0.0.0:3333", "use_tls": False},
    "phish_server": {"listen_url": "0.0.0.0:8080", "use_tls": False},
    "migrations_prefix": "db/db_",
    "contact_address": "DL_TSA@godaddy.com",
    "logging": {"filename": "", "level": ""},
}

try:
    AWS_ACCOUNT = boto3.client("sts").get_caller_identity()["Account"]

    DB_ENDPOINT = boto3.client("ssm", region_name="us-west-2").get_parameter(
        Name="/Team/Aurora/gophish/Address"
    )["Parameter"]["Value"]

    DB_USER_CREDS = json.loads(
        boto3.client("secretsmanager", region_name="us-west-2").get_secret_value(
            SecretId="arn:aws:secretsmanager:us-west-2:%s:secret:GophishDBUserCredentials"
            % AWS_ACCOUNT
        )["SecretString"]
    )

    gophish_config["db_name"] = "mysql"
    gophish_config[
        "db_path"
    ] = "%s:%s@(%s:3306)/gophish?charset=utf8&parseTime=True&loc=UTC" % (
        DB_USER_CREDS["username"],
        DB_USER_CREDS["password"],
        DB_ENDPOINT,
    )

except Exception:
    log.exception("Error retrieving GoPhish configuration!")
    # Fall back to local sqlite3 database
    gophish_config["db_name"] = "sqlite3"
    gophish_config["db_path"] = "gophish.db"

config_content = json.dumps(gophish_config, indent=2)

open("config.json", "w").write(config_content)

log.info("Configuration: %s", json.dumps(gophish_config))

GOPHISH_MODE = os.getenv("MODE", "all")
log.info("Mode: %s", GOPHISH_MODE)

os.system("./gophish --mode=%s" % GOPHISH_MODE)
