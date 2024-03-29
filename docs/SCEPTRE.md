# Environment Setup

### Python Environment

1. Create and activate a python3 virtual environment with modules listed in the
   `requirements.txt` file:

   ```
   python3.8 -m venv venv
   source venv/bin/activate
   pip install -U pip
   pip install -U -r requirements.txt -r requirements-test.txt
   ```

1. Activate the virtualenv:

   ```
   source venv/bin/activate
   ```

1. Authenticate using the service account:

   * Login with your Jomax credentials by following the directions
     [here](https://github.com/godaddy/aws-okta-processor).

     To manually obtain an assumed role for your Jomax account:

     ```
     eval $(aws-okta-processor authenticate -d 7200 -e -o godaddy.okta.com -u ${USER} -k okta)
     ```

   * Verify your current role:

     ```
     aws sts get-caller-identity
     ```

   * Obtain an assumed deployment role using the deploy user credentials from
     SecretsManager:

     ```
     DEPLOY_USER=$(aws secretsmanager get-secret-value \
                       --secret-id /Secrets/IAMUser/GD-AWS-DeployUser-Phish-Dev-Private \
                       --query SecretString \
                       --output text)

     export AWS_ACCESS_KEY_ID="$(echo $DEPLOY_USER | jq -r .AccessKeyId)"
     export AWS_SECRET_ACCESS_KEY="$(echo $DEPLOY_USER | jq -r .SecretAccessKey)"
     export AWS_DEFAULT_REGION="us-west-2"
     unset AWS_SESSION_TOKEN

     DEPLOY_ROLE=$(aws sts assume-role \
                       --role-arn arn:aws:iam::911872167152:role/GD-AWS-USA-CTO-Phish-Dev-Private-Deploy \
                       --role-session-name $(git config user.email) \
                       --output text \
                       --query '[Credentials.AccessKeyId, Credentials.SecretAccessKey, Credentials.SessionToken]')

     export AWS_ACCESS_KEY_ID=$(echo ${DEPLOY_ROLE} | cut -d' ' -f1)
     export AWS_SECRET_ACCESS_KEY=$(echo ${DEPLOY_ROLE} | cut -d' ' -f2)
     export AWS_SESSION_TOKEN=$(echo ${DEPLOY_ROLE} | cut -d' ' -f3)
     ```

   * Verify you now have the deployment role:

     ```
     aws sts get-caller-identity
     ```

### AWS Certificate Manager (ACM) Setup

1. Use [Cloud UI](https://cloud.int.godaddy.com/security/certs) to request a
   certificate for the FQDN to be used by the **admin** interface, such as
   `admin.phish.int.dev-gdcorp.tools`.

1. Use [Cloud UI](https://cloud.int.godaddy.com/security/certs) to request a
   certificate for the FQDN to be used by the **status** interface, such as
   `phish.int.dev-gdcorp.tools`.

1. For each certificate requested above, download the certificate, private key,
   and certificate chain from Cloud UI to your local workstation.

1. Run the following using the deployment role, such as
   `GD-AWS-USA-CTO-Phish-Dev-Private-Deploy`:

   * DEV-PRIVATE

   ```
   aws acm import-certificate \
       --certificate file://admin.phish.int.dev-gdcorp.tools.crt \
       --private-key file://admin.phish.int.dev-gdcorp.tools.key \
       --certificate-chain file://admin.phish.int.dev-gdcorp.tools_intermediate_chain.crt

   aws acm import-certificate \
       --certificate file://phish.int.dev-gdcorp.tools.crt \
       --private-key file://phish.int.dev-gdcorp.tools.key \
       --certificate-chain file://phish.int.dev-gdcorp.tools_intermediate_chain.crt
   ```

   * PROD

   ```
   aws acm import-certificate \
       --certificate file://admin.phish.int.gdcorp.tools.crt \
       --private-key file://admin.phish.int.gdcorp.tools.key \
       --certificate-chain file://admin.phish.int.gdcorp.tools_intermediate_chain.crt

   aws acm import-certificate \
       --certificate file://phish.int.gdcorp.tools.crt \
       --private-key file://phish.int.gdcorp.tools.key \
       --certificate-chain file://phish.int.gdcorp.tools_intermediate_chain.crt
   ```

1. Delete the downloaded copies of the certificate, private key, and
   certificate chain from your local workstation.

1. Note the UUID contained in the `CertificateArn` that is displayed when each
   certificate is imported.  These values should match those specified by
   `gophish_certificate_id` and `status_certificate_id` in the Sceptre
   configuration file for the current environment.  N.B. the
   `landing_certificate_id` is used by the phishing landing page and is
   described [here](PLAYBOOKS.md#phish-domain-configuration).

### Sceptre / CloudFormation / Service Catalog

Run sceptre to configure the AWS account (substituting the appropriate
environment):

```
cd sceptre

# Create ECR repository
sceptre launch dev-private/us-west-2/SC-Repositories.yaml

# Build gophish container
pushd ../containers/gophish/
aws ecr get-login-password --region us-west-2 | sudo docker login --username AWS --password-stdin 764525110978.dkr.ecr.us-west-2.amazonaws.com
sudo docker build --pull -t gophish .

# Upload gophish container
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region us-west-2 | sudo docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com
sudo docker tag gophish:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/gophish:latest
sudo docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/gophish:latest
popd

# Deploy remaining Gophish infrastructure
sceptre launch dev-private/us-west-2
```

### Update DNS CNAME Entries

1. Use [Cloud UI](https://cloud.int.godaddy.com/networking/dnsrecords) to
   create or update a `CNAME` DNS record for the specified FQDN of the Gophish
   administrative interface.  It should reference the `DNSName` of the newly
   created `gophish` load balancer.  The target of the CNAME record should
   match the output of:

   ```
   aws elbv2 describe-load-balancers \
       --names gophish \
       --query 'LoadBalancers[].DNSName' \
       --output text
   ```

1. Use [Cloud UI](https://cloud.int.godaddy.com/networking/dnsrecords) to
   create or update a `CNAME` DNS record for the specified FQDN of the Gophish
   status page.  It should reference the `DNSName` of the newly created
   `status` load balancer.  The target of the CNAME record should match the
   output of:

   ```
   aws elbv2 describe-load-balancers \
       --names status \
       --query 'LoadBalancers[].DNSName' \
       --output text
   ```
