# PhishFramework Architecture

The [Gophish](https://getgophish.com/) software provides two primary functions:

* An administrative interface, where a Gophish administrator manages campaigns
  and views metrics
* A webserver that serves arbitrary phishing sites

### Gophish Services

The infrastructure configured by the GoDaddy PhishFramework consists of three
different services:

| Service                             | Type               | Auth             | URL (Dev-Private)                        |
|-------------------------------------|--------------------|------------------|------------------------------------------|
| [Gophish Admin](#gophish-admin)     | Private (Internal) | Gophish built-in | https://admin.phish.int.dev-gdcorp.tools |
| [Gophish Landing](#gophish-landing) | Public (External)  | None             | https://okta.gocladdy.com (varies)       |
| [Gophish Status](#gophish-status)   | Private (Internal) | SSO JWT          | https://phish.int.dev-gdcorp.tools       |

### AWS Components

![Gophish Overview](diagrams/PhishFramework.png "Gophish Overview")

### Gophish Admin

The **Gophish Admin** service consists of a private application load balancer
that forwards traffic to the `admin` service provided by the Gophish
application.  The Gophish application runs as a Fargate task (named `gophish`)
using the [gophish](../containers/gophish/) container image.  The container
reads parameters at startup to determine the MySQL endpoint that should be
used.

### Gophish Landing

The **Gophish Landing** service consists of a public application load balancer
that forwards traffic to the `phish` service provided by the Gophish
application.  The Gophish application runs as a Fargate task (named `landing`)
using the [gophish](../containers/gophish/) container image.  The container
reads parameters at startup to determine the MySQL endpoint that should be
used.

### Gophish Status

The **Gophish Status** service consists of a private application load balancer
that forwards traffic to a Python lambda function.  The lambda function checks
for the presence of a valid Jomax JWT.  If a valid JWT is not present, the user
is redirected to the SSO login page.  Otherwise, an API call is made to the
*Gophish Admin* service to query both active and archived campaigns.  The
summarized campaign information is presented to the caller via a simple HTML
table.  At present, the user is not able to interact with the Gophish service
in any way other than a read-only retrieval of campaign statistics.
