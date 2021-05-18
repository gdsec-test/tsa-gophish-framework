#!/bin/bash

DB_ENDPOINT=$(aws ssm get-parameter --name /Team/Aurora/gophish/Address --query Parameter.Value --output text)
DB_ADMIN_CREDS=$(aws secretsmanager get-secret-value --secret-id gophish --query SecretString --output text)

admin_username="$(echo $DB_ADMIN_CREDS | jq -r .username)"
admin_password="$(echo $DB_ADMIN_CREDS | jq -r .password)"

mysql --host="${DB_ENDPOINT}" --user="${admin_username}" --password="${admin_password}" gophish << _EOF

UPDATE email_requests
   SET email = MD5(email),
       first_name = '', last_name = '', position = ''
 WHERE email like '%@%';

UPDATE events
   SET email = MD5(email),
       details = ''
 WHERE email LIKE '%@%';

UPDATE results
   SET email = MD5(email),
       first_name = '', last_name = '', ip = '', latitude = 0, longitude = 0
 WHERE email LIKE '%@%';

UPDATE targets
   SET email = MD5(email),
       first_name = '', last_name = '', position = ''
 WHERE email LIKE '%@%';

_EOF
