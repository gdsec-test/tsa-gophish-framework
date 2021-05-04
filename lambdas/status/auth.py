"""Validate a JWT contained within a request event"""

import datetime
from http import cookies
import json
import logging
import os

from gd_auth.token import AuthToken, TokenBusinessLevel

log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)

SSO_HOST = os.getenv("SSO_HOST", "sso.gdcorp.tools")


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

    except Exception:  # pylint: disable=broad-except
        # Don't care what the exception is; don't allow access
        log.exception("Unable to parse auth_jomax cookie:")
        return False

    # AuthToken.parse() returned None for some reason; reject the cookie
    log.error("Invalid auth_jomax cookie")
    return False
