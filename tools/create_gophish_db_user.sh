#!/bin/bash

DB_ENDPOINT=$(aws ssm get-parameter --name /Team/Aurora/gophish/Address --query Parameter.Value --output text)
DB_ADMIN_CREDS=$(aws secretsmanager get-secret-value --secret-id gophish --query SecretString --output text)
DB_USER_CREDS=$(aws secretsmanager get-secret-value --secret-id GophishDBUserCredentials --query SecretString --output text)

admin_username="$(echo $DB_ADMIN_CREDS | jq -r .username)"
admin_password="$(echo $DB_ADMIN_CREDS | jq -r .password)"

gophish_username="$(echo $DB_USER_CREDS | jq -r .username)"
gophish_password="$(echo $DB_USER_CREDS | jq -r .password)"

mysql --host="${DB_ENDPOINT}" --user="${gophish_username}" --password="${gophish_password}" gophish < /dev/null

if [ "$?" != "0" ]; then
mysql --host="${DB_ENDPOINT}" --user="${admin_username}" --password="${admin_password}" << _EOF
CREATE DATABASE gophish CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
create user "${gophish_username}" identified by "${gophish_password}";
grant all on gophish.* to "gophish";
flush privileges;
_EOF
fi
