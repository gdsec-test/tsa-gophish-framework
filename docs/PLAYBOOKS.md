# PhishFramework Playbooks

The steps outlined in this document may be useful to developers or support
personnel while additional tools and processes are under development.

### Contents

* [Deploying a new Gophish container build](#deploying-a-new-gophish-container-build)
* [Deploying a new status lambda](#deploying-a-new-status-lambda)
* [Phish domain configuration](#phish-domain-configuration)

### Deploying a new Gophish container build

The Gophish service is distributed as a standalone binary from the [Gophish
Releases Page](https://github.com/gophish/gophish/releases) on GitHub.  At the
moment, a binary build is used since GoDaddy does not (yet) make any
modifications to the Gophish source code.  The [container
documentation](../containers/gophish/README.md) provides some additional
details.  The automation of this container build will eventually use GitHub
Actions, but the following steps should be followed for now:

1. Use `aws ecr get-login-password` to authenticate to AWS, allowing you to
   pull the Golden Container image that's used by this container.

1. Build the container using `docker build`.

1. Upload the container to ECR using `docker push`.

1. Force a new deployment of the ECS service using `aws ecs update-service`.

### Deploying a new status lambda

The status lambda provides a simple HTML report for GoDaddy employees that
shows high level statistics regarding current and previous phishing campaigns.
Updates to this lambda will eventually use GitHub Actions, but the following
steps should be followed for now:

**Using Sceptre**

1. Obtain deploy role credentials (see [Infrastructure Setup /
   Provisioning](SCEPTRE.md))

1. Use `sceptre launch dev-private/us-west-2` (substitute appropriate
   environment)

**Using manual steps**

1. Change to the lambda source directory:

   ```
   cd ../lambdas/status/
   ```

1. Build the lambda:

   ```
   ./build.sh
   ```

1. Update the lambda code in AWS:

   ```
   ./update.sh
   ```

**Cached build considerations**

The lambda build process attempts to reuse a previous build if both
`function.zip` and `lambda.sha1` are found in the current directory.  To force
a rebuild of the lambda, remove these files before performing the build, e.g.:

```
cd ../lambdas/status/
rm -f function.zip lambda.sha1
./build.sh
./update.sh
```

### Phish domain configuration

Gophish sends phishing emails to users that contain links to a "landing" page
containing a fake login page or some other form requesting credentials.  An
example of a landing page used in previous campaigns would be
`okta.gocladdy.com` (using a `c` and `l` instead of the expected `d` for the
phishing domain).

The landing page is configured by the Sceptre templates and Service Catalog
products to redirect any HTTP access to the corresponding HTTPS URL, so any
users requesting http://okta.gocladdy.com/some-url would be automatically
redirected to https://okta.gocladdy.com/some-url.  The certificate for the
landing page must exist in [Certificate
Manager](https://us-west-2.console.aws.amazon.com/acm/home?region=us-west-2#/),
and can either be issued by AWS or imported if the certificate was issued by
GoDaddy and obtained using e.g. Cloud UI.

To configure a certificate for use by a landing page, follow these steps:

1. Use AWS Certificate Manager to either generate a certificate issued by AWS,
   or import a certificate issued by GoDaddy.

1. Specify the Certificate ARN for the above certificate as
   `landing_certificate_id` in the Sceptre configuration file for the specific
   environment, for example:

   ```
   $ vi landing_certificate_id sceptre/config/dev-private/us-west-2/config.yaml
   ...
   landing_certificate_id: b70feb74-94e0-4f34-8e5b-5205232b29a4
   ...
   ```

1. Run sceptre for the given environment.  See [Infrastructure Setup /
   Provisioning](SCEPTRE.md) for more information.

1. Specify the URL for the landing page when creating a new Gophish campaign.
   See [Creating the Landing
   Page](https://docs.getgophish.com/user-guide/building-your-first-campaign/creating-the-landing-page)
   for more information from the Gophish documentation.

1. Create or update a **DNS CNAME** entry corresponding to the landing page,
   setting its value to the DNS name of the load balancer created by the
   Sceptre invocation:

   ```
   aws elbv2 describe-load-balancers \
       --names landing \
       --query 'LoadBalancers[].DNSName' \
       --output text
   ```
