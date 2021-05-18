# PhishFramework Playbooks

This project will support the CTO / InfoSec goal of running security exercises
using a phishing framework (initially, GoPhish) that can be used to measure
security training effectiveness on GoDaddy employees.

This project is a Tier 4 service.

## General Oncall/Operational Info

### Contact information

* ServiceNow Oncall group: `Eng-TSA`
* Email distribution list: `DL_TSA@godaddy.com`
* Contact group: TSA (InfoSec) - Philipp Sonntag
* Partner groups: SRA (InfoSec)

### GitHub repositories

* [tsa-gophish-framework](https://github.com/gdcorp-infosec/tsa-gophish-framework)
* [gophish: Open-Source Phishing Toolkit](https://github.com/gophish/gophish)

### URLs

* DEV-PRIVATE

  * [Gophish Administrative Interface](https://admin.phish.int.dev-gdcorp.tools/) (internal)
  * [Security Exercise Status Page](https://phish.int.dev-gdcorp.tools/) (internal, requires SSO)
  * Phishing Landing Page: https://landing.phish.gdcorp.tools (external)

* TEST

  TBD

* PROD

  TBD

## Architecture Overview

### Diagrams

* [Functional Diagram](https://github.com/gdcorp-infosec/tsa-gophish-framework/blob/main/docs/ARCHITECTURE.md)
* [Dependency Diagram](https://github.com/gdcorp-infosec/tsa-gophish-framework/blob/main/docs/ARCHITECTURE.md#gophish-dependency-diagram)
* [Sequence Diagram](https://github.com/gdcorp-infosec/tsa-gophish-framework/blob/main/docs/ARCHITECTURE.md#gophish-sequence-diagram)
* [Data Diagram](https://github.com/gdcorp-infosec/tsa-gophish-framework/blob/main/docs/ARCHITECTURE.md#gophish-data-diagram)
* [Deployment Diagram](https://github.com/gdcorp-infosec/tsa-gophish-framework/blob/main/docs/ARCHITECTURE.md#gophish-deployment-diagram)
* [Gophish API Documentation](https://docs.getgophish.com/api-documentation/)

### CICD / GitHub Actions

The following GitHub actions workflows are configured for this repository:

* [Code quality check](../.github/workflows/code-check.yml)

  * Triggers on every Pull Request made to the `main` branch
  * Runs Tartufo as the first check
  * On success of Tartufo, triggers `python-code-check` job

* [Container Rotation](../.github/workflows/rotate-containers.yml)

  * Triggered daily at 3:08 AM UTC (or manually)
  * Forces an update of the Gophish ECS service to force container rotations

* [Deployment (DEV-PRIVATE)](../.github/workflows/deploy-to-dev-private.yml)

  * Triggered manually
  * Runs sceptre to deploy DEV-PRIVATE environment

## Monitoring

* [Kibana Dashboard (non-prod)](https://phish-non-prod.kibana.int.gdcorp.tools/app/home#/)

Gophish logs are can be found in the following Cloudwatch Log groups:

* `/ecs/gophishTaskDefinition`

  This log group contains logs for the `admin` service, which provides the
  administrative interface to manage campaigns, users, templates, etc.

* `/ecs/landingTaskDefinition`

  This log group contains logs for the `phish` service, which serves the
  phishing web pages ("landing pages") that users will see if they click links
  in the phishing emails.  Visits to this page update the Gophish database to
  record which users opened emails, clicked links, and provided credentials.

## Alerts

*TBD*

Goal is to document the alerts that exist, or will, and include
remediation/troubleshooting information specific to those alert scenarios,
impact scope, relevant metrics related to alert where applicable, etc. -
typical Knowledge Base type information

## Communication and Escalation Workflows

*TBD*

Goal is to document escalation and communications procedures where applicable

## Other Information

The below steps may be useful to developers or support personnel while
additional tools and processes are under development.

* [Backup and Restore operations](#backup-and-restore-operations)
* [Recovery process](#recovery-process)
* [Deploying a new Gophish container build](#deploying-a-new-gophish-container-build)
* [Deploying a new status lambda](#deploying-a-new-status-lambda)
* [Phish domain configuration](#phish-domain-configuration)

### Backup and Restore operations

The following tools can be used to perform backup and restore operations with
the Gophish database.  Both tools require AWS credentials that allow reading
the MySQL database credential information from AWS Secrets Manager.

* [tools/dump_database.sh](../tools/dump_database.sh)

  This utility obtains database credentials from AWS Secrets Manager and then
  initiates a MySQL connection to the Gophish database.  It then dumps the
  database using `mysqldump` to the console.  The output can be redirected to a
  file, and later used as input for the following tool to restore the Gophish
  database if necessary.

* [tools/load_database.sh](../tools/load_database.sh)

  This utility obtains database credentials from AWS Secrets Manager and then
  initiates a MySQL connection to the Gophish database.  It then provides a
  MySQL prompt for diagnostics or troubleshooting.  A database dump produced by
  the above script can be passed as input to this tool to restore a previous
  Gophish database backup.

### Recovery process

As a tier 4 service, the phishing framework does not have any automated
recovery processes beyond that provided by the various AWS services
(Application Loadbalancers, Aurora serverless RDS, Lambda, and ECS).  The
following steps should be taken if the Gophish environment needs to be
recovered to a known good state:

1. Perform a sceptre run by following the [Gophish environment
   setup](SCEPTRE.md) instructions, or by manually triggering a deployment
   workflow using GitHub actions.

1. Restore a known good Gophish database backup using the `load_database.sh`
   tool described above.

1. If the database has been reset, and you don't wish to use (or don't have) a
   known good backup to restore from, then you'll need to obtain the randomized
   password for the `admin` user that's generated automatically by the Gophish
   admin service.  The `admin` service will output the temporary randomized
   password in the `/ecs/gophishTaskDefinition` Cloudwatch log group if the
   database is not already configured.  You'll then need to access the
   administrative interace using this password and change the credentials for
   the administrator.

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
Updates to the lambda code will be deployed automatically via GitHub Actions,
but the following steps may be used in the dev-private environment by
developers for testing modifications:

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
