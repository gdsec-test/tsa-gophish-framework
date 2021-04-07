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
   certificate for the FQDN to be used, such as
   `admin.phish.int.dev-gdcorp.tools`.

1. Download the certificate, private key, and certificate chain from Cloud UI
   to your local workstation.

1. Run the following using the deployment role, such as
   `GD-AWS-USA-CTO-Phish-Dev-Private-Deploy`:

   * DEV-PRIVATE

   ```
   aws acm import-certificate \
       --certificate file://admin.phish.int.dev-gdcorp.tools.crt \
       --private-key file://admin.phish.int.dev-gdcorp.tools.key \
       --certificate-chain file://admin.phish.int.dev-gdcorp.tools_intermediate_chain.crt
   ```

   * PROD

   ```
   aws acm import-certificate \
       --certificate file://admin.phish.int.gdcorp.tools.crt \
       --private-key file://admin.phish.int.gdcorp.tools.key \
       --certificate-chain file://admin.phish.int.gdcorp.tools_intermediate_chain.crt
   ```

1. Delete the downloaded copies of the certificate, private key, and
   certificate chain from your local workstation.

1. Note the UUID contained in the `CertificateArn` that is displayed when the
   certificate is imported.  This value should match that specified by
   `gophish_certificate_id` in the Sceptre configuration file for the current
   environment.

### Sceptre / CloudFormation / Service Catalog

Run sceptre to configure the AWS account (substituting the appropriate
environment):

```
cd sceptre
sceptre launch dev-private/us-west-2
```

### Update DNS CNAME Entry

1. Use [Cloud UI](https://cloud.int.godaddy.com/networking/dnsrecords) to
   create or update a `CNAME` DNS record for the specified FQDN that points to
   the `DNSName` of the newly created `gophish` load balancer.  The target of
   the CNAME record should match the output of:

   ```
   aws elbv2 describe-load-balancers \
       --names gophish \
       --query 'LoadBalancers[].DNSName' \
       --output text
   ```
