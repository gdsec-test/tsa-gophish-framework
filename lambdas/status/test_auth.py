import unittest
from unittest.mock import patch

import copy
import importlib
import os

import auth

# The following sample event is not complete; some high entropy entries have
# been removed.

EVENT_TEMPLATE = {
    "requestContext": {
        "elb": {
            "targetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/status/0123456789abcdef"
        }
    },
    "httpMethod": "GET",
    "path": "/",
    "queryStringParameters": {},
    "headers": {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.5",
        "cache-control": "max-age=0",
        "connection": "keep-alive",
        "cookie": "key1=value1; key2=value2",
        "host": "phish.int.dev-gdcorp.tools",
        "referer": "https://godaddy.okta.com/app/godaddyprod_gdcorpssodev_1/aaa/sso/saml",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "x-amzn-trace-id": "Root=1-00000000-000000000000000000000000",
        "x-forwarded-for": "10.39.80.70",
        "x-forwarded-port": "443",
        "x-forwarded-proto": "https",
    },
    "body": "",
    "isBase64Encoded": False,
}


class status_lambda_tests(unittest.TestCase):
    @patch.dict(os.environ, {})
    def test_sso_endpoint_default(self):
        importlib.reload(auth)

        self.assertEqual(auth.SSO_HOST, "sso.gdcorp.tools")

    @patch.dict(os.environ, {"SSO_HOST": "sso.dev-gdcorp.tools"})
    def test_sso_endpoint_override(self):
        importlib.reload(auth)

        self.assertEqual(auth.SSO_HOST, "sso.dev-gdcorp.tools")

    @patch.dict(os.environ, {"SSO_HOST": "sso.custom.endpoint"})
    @patch("auth.AuthToken.parse")
    def test_valid_jwt_valid(self, mock_authtoken_parse):
        response = {
            "ftc": 2,
            "factors": {"k_fed": 1620147104, "p_okta": 1620147104},
            "accountName": "testuser1",
            "iat": 1620147104,
        }
        mock_authtoken_parse.return_value.payload = response

        importlib.reload(auth)

        event = copy.deepcopy(EVENT_TEMPLATE)
        event["headers"][
            "cookie"
        ] = "key1=value1;auth_jomax=fake.cookie.jwt;key2=value2"

        rc = auth.valid_jwt(event)

        mock_authtoken_parse.assert_called_once_with(
            "fake.cookie.jwt",
            "sso.custom.endpoint",
            app="PhishStatus",
            typ="jomax",
            level=2,
        )

        self.assertEqual(rc, True)

    @patch.dict(os.environ, {"SSO_HOST": "sso.custom.endpoint"})
    @patch("auth.AuthToken.parse")
    def test_valid_jwt_missing_cookie(self, mock_authtoken_parse):
        importlib.reload(auth)

        event = copy.deepcopy(EVENT_TEMPLATE)
        event["headers"]["cookie"] = "key1=value1;key2=value2"

        rc = auth.valid_jwt(event)

        mock_authtoken_parse.assert_not_called()

        self.assertEqual(rc, False)

    @patch.dict(os.environ, {"SSO_HOST": "sso.custom.endpoint"})
    @patch("auth.AuthToken.parse")
    def test_valid_jwt_exception(self, mock_authtoken_parse):
        mock_authtoken_parse.side_effect = Exception("bang!")

        importlib.reload(auth)

        event = copy.deepcopy(EVENT_TEMPLATE)
        event["headers"][
            "cookie"
        ] = "key1=value1;auth_jomax=fake.cookie.jwt;key2=value2"

        rc = auth.valid_jwt(event)

        self.assertEqual(rc, False)

    @patch.dict(os.environ, {"SSO_HOST": "sso.custom.endpoint"})
    @patch("auth.AuthToken.parse")
    def test_valid_jwt_empty_result(self, mock_authtoken_parse):
        mock_authtoken_parse.return_value = None

        importlib.reload(auth)

        event = copy.deepcopy(EVENT_TEMPLATE)
        event["headers"][
            "cookie"
        ] = "key1=value1;auth_jomax=fake.cookie.jwt;key2=value2"

        rc = auth.valid_jwt(event)

        self.assertEqual(rc, False)
