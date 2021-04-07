#!/usr/bin/env python3

"""\
GoDaddy Security Exercise Status page

This page directly renders HTML that enumerates any active and archived Gophish
campaigns.
"""

import datetime
from http import cookies
import json
import logging
import os
from textwrap import dedent

import boto3
from gophish import Gophish

from gd_auth.token import AuthToken, TokenBusinessLevel

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
    </body>
    </html>
    """
)

SSO_HOST = os.getenv("SSO_HOST", "sso.gdcorp.tools")


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


def valid_jwt(event):
    """Make sure the request header includes a valid JWT"""

    # Check for existing auth_jomax cookie
    try:
        cookie_header = event["headers"]["cookie"]
        jwt = cookies.SimpleCookie(cookie_header)["auth_jomax"].value

    except KeyError:
        log.error("No auth_jomax cookie present")
        return False

    # Validate provided auth_jomax cookie
    try:
        auth_token = AuthToken.parse(
            jwt,
            SSO_HOST,
            app="PhishStatus",
            typ="jomax",
            level=TokenBusinessLevel.MEDIUM,
        )
        if auth_token:
            log.debug("ftc: %d", auth_token.payload["ftc"])
            log.debug("factors: %s", json.dumps(auth_token.payload["factors"]))
            log.debug("accountName: %s", auth_token.payload["accountName"])

            iat = auth_token.payload["iat"]
            iat_str = datetime.datetime.fromtimestamp(
                iat, tz=datetime.timezone.utc
            ).isoformat()
            log.debug("iat: %d (%s)", iat, iat_str)

            return True

    except Exception:
        log.exception("Unable to parse auth_jomax cookie:")
        return False

    # AuthToken.parse() returned None for some reason; reject the cookie
    log.error("Invalid auth_jomax cookie")
    return False


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
        result = {"statusCode": 500, "body": "Internal Server Error"}

    return result


if __name__ == "__main__":
    handler(None, None)
