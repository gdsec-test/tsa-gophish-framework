# Gophish container

## Build container

```
# https://confluence.godaddy.com/display/AS/Onboarding+How+To
aws ecr get-login-password --region us-west-2 | sudo docker login --username AWS --password-stdin 764525110978.dkr.ecr.us-west-2.amazonaws.com
sudo docker build --pull -t gophish .
```

## Debugging (shell)

```
# Enter the docker container:
sudo docker run --rm -it gophish /bin/bash

# Run Gophish
./run.py
```

## Local execution

```
# Run the docker container:
sudo docker run -d -p 3333:3333 -p 8080:8080 --name gophish gophish

# Get logs to see admin password:
sudo docker logs gophish

# Stop the docker container:
sudo docker stop gophish
sudo docker rm gophish
```

## Upload container

```
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region us-west-2 | sudo docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com
sudo docker tag gophish:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/gophish:latest
sudo docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/gophish:latest
```
