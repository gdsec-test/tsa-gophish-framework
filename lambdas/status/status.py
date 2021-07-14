"""\
GoDaddy Security Exercise Status page

This page directly renders HTML that enumerates any active and archived Gophish
campaigns.
"""

import json
import logging
import os
from textwrap import dedent

import boto3
from gophish import Gophish
from auth import valid_jwt

log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)

AWS_ACCOUNT = boto3.client("sts").get_caller_identity()["Account"]

GOPHISH_API = json.loads(
    boto3.client("secretsmanager", region_name="us-west-2").get_secret_value(
        SecretId="arn:aws:secretsmanager:us-west-2:%s:secret:GophishAPI" % AWS_ACCOUNT
    )["SecretString"]
)

GOPHISH_API_KEY = GOPHISH_API["api_key"]
GOPHISH_API_URL = GOPHISH_API["api_url"]

HTML_HEADER = dedent(
    """\
    <!DOCTYPE HTML>
    <html>
    <head>
    <meta charset="utf-8"/>
    <title>GoDaddy Security Exercise Status</title>
    <style>
      a {
        color: #909090;
      }
      body {
        background-color: #202020;
        color: #909090;
        font-family: Arial, Helvetica, sans-serif;
        margin: auto;
        max-width: 960px;
      }
      h1 {
        margin: 75px 0px 15px 0px;
      }
      table {
        width: 100%;
      }
      tr:hover {
        background-color: #303030;
      }
      th {
        text-align: left;
        padding: 15px;
      }
      td {
        padding: 15px;
      }
      th, td {
        border-bottom: 1px solid #909090;
      }
      #active_banner {
        border: 3px solid #C04040;
        color: #C04040;
        font-size: 2.5em;
        font-weight: bold;
        margin: 50px 0px;
        max-width: 100%;
        padding: 15px; 50px;
        text-align: center;
      }
      #inactive_banner {
        border: 3px solid #40C040;
        color: #40C040;
        font-size: 2.5em;
        font-weight: normal;
        margin: 50px 0px;
        max-width: 100%;
        padding: 15px; 50px;
        text-align: center;
      }
    </style>
    </head>
    <body>
    """
)

HTML_FOOTER = dedent(
    """\
    <h1>Privacy Notice</h1>
    <p>
      GoDaddy's Social Engineering Assessment (SEA) Platform is a tool utilized
      by our InfoSec team to provide transparency into our employee training
      efforts, including aggregated data that monitors the effectiveness of
      these assessments, which are critical to helping us properly recognize
      and handle deceptive phishing email from threat actors. We all must
      remain vigilant against these threat actors to be trusted partners for
      our everyday entrepreneurs. We do not capture or store your credentials
      in the SEA Platform and ensure that all assessments are conducted in a
      manner consistent with our
      <a href="https://godaddy.service-now.com/gdep/?id=gdep_kb_article&sysparm_article=KB0014214">Employee Privacy policy</a>
      and local staff handbooks, as applicable.
    </p>
    <h2>Metrics</h2>
    <p>
    Please note that the <i>Clicked Link</i> and <i>Email Opened</i> metrics reflect
    the number of emails sent due to Security tooling that automatically evaluates
    links in emails; this does not reflect the actual count of clicked links or opened
    emails. We are working towards addressing those metrics.
    </p>
    </body>
    </html>
    """
)

SSO_HOST = os.getenv("SSO_HOST", "sso.gdcorp.tools")

HTML_UNAVAILABLE = (
    HTML_HEADER
    + '<div id="active_banner">Security exercise status unavailable</div>\n'
    + HTML_FOOTER
)


def stat_summaries(campaigns):
    """Generate HTML containing statistics for a list of campaigns"""

    log.debug("Name,Email Sent,Email Opened,Clicked Link,Submitted Data")
    html = "<table>\n"
    html += "<tr><th>Name</th><th>Launch Date</th><th>Email Sent</th><th>Email Opened</th><th>Clicked Link</th><th>Submitted Data</th></tr>\n"

    for c in sorted(campaigns, key=lambda x: x.launch_date, reverse=True):
        log.debug(
            "%s,%s,%d,%d,%d,%d",
            c.name,
            c.launch_date,
            c.stats.sent,
            c.stats.opened,
            c.stats.clicked,
            c.stats.submitted_data,
        )

        if c.stats.total > 0:
            html += "<tr><td>%s</td><td>%s</td><td>%d (%.1f%%)</td><td>%d (%.1f%%)</td><td>%d (%.1f%%)</td><td>%d (%.1f%%)</td></tr>\n" % (
                c.name,
                c.launch_date,
                c.stats.sent,
                100.0 * (c.stats.sent / c.stats.total),
                c.stats.opened,
                100.0 * (c.stats.opened / c.stats.total),
                c.stats.clicked,
                100.0 * (c.stats.clicked / c.stats.total),
                c.stats.submitted_data,
                100.0 * (c.stats.submitted_data / c.stats.total),
            )

    html += "</table>\n"

    return html


def handler(event, context):
    """Default lambda handler"""

    if event.get("path") == "/healthcheck":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": "OK",
        }

    if not valid_jwt(event):
        return {
            "statusCode": 302,
            "headers": {
                "Location": "https://%s/login?realm=jomax&app=phish.int" % SSO_HOST
            },
        }

    try:
        #       gophish_key, gophish_url = get_gophish_api

        api = Gophish(GOPHISH_API_KEY, host=GOPHISH_API_URL)

        summaries = api.campaigns.summary()

        active_campaigns = [c for c in summaries.campaigns if c.status == "In progress"]
        archived_campaigns = [c for c in summaries.campaigns if c.status == "Completed"]

        html = HTML_HEADER

        if active_campaigns:
            html += (
                '<div id="active_banner">Active security exercise in progress!</div>\n'
            )
        else:
            html += '<div id="inactive_banner">No security exercise currently in progress</div>\n'

        if active_campaigns:
            log.debug("Active campaigns:")
            html += "<h1>Active campaigns</h1>\n"
            html += stat_summaries(active_campaigns)

        if archived_campaigns:
            log.debug("Archived campaigns:")
            html += "<h1>Archived campaigns</h1>\n"
            html += stat_summaries(archived_campaigns)

        html += HTML_FOOTER

        result = {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": html,
        }

    except Exception:
        log.exception("Unable to retrieve gophish status")
        result = {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": HTML_UNAVAILABLE,
        }

    return result
