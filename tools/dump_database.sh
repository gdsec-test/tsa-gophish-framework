#!/bin/bash

DB_ENDPOINT=$(aws ssm get-parameter --name /Team/Aurora/gophish/Address --query Parameter.Value --output text)
DB_ADMIN_CREDS=$(aws secretsmanager get-secret-value --secret-id gophish --query SecretString --output text)

admin_username="$(echo $DB_ADMIN_CREDS | jq -r .username)"
admin_password="$(echo $DB_ADMIN_CREDS | jq -r .password)"

mysqldump --host="${DB_ENDPOINT}" --user="${admin_username}" --password="${admin_password}" gophish
