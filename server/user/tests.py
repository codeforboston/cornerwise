from django.test import Client, TestCase, tag, override_settings
from django.urls import reverse
from django.conf import settings
from django.core import mail
from django.core.exceptions import ValidationError

from django.contrib.auth import authenticate, get_user_model
from django.contrib.gis.measure import D

import json
import random
import re
from urllib.parse import parse_qs, urlsplit

from . import models, views, mail_parse_views
from .models import Subscription, UserComment, UserProfile
import site_config

import warnings
warnings.filterwarnings(
    'ignore', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields')

User = get_user_model()


LAT_SW = 42.372305415983895
LNG_SW = -71.14256858825685
LAT_NE = 42.41635997208289
LNG_NE = -71.06600761413576

regions = ["Somerville, MA", "Cambridge, MA"]

def rand_point():
    return (random.uniform(LAT_SW, LAT_NE),
            random.uniform(LNG_SW, LNG_NE))


def add_box(q):
    (swlat, swlng) = rand_point()
    nelat = random.uniform(swlat, LAT_NE)
    nelng = random.uniform(swlng, LNG_NE)
    q["box"] = f"{swlat},{swlng},{nelat},{nelng}"
    return q


def add_radius(q):
    q["center"] = ",".join(map(str, rand_point()))
    q["r"] = D(ft=300).m
    return q


def rand_query():
    query = {}
    if random.random() >= 0.5:
        add_box(query)
    else:
        add_radius(query)

    query["region"] = random.choice(regions)

    return query


def get_links(html):
    for m in re.finditer(r"href=\"([^\"]+)\"", html, re.I):
        parts = urlsplit(m.group(1))
        yield f"{parts.path}?{parts.query}"



# Decorator to override celery settings during tests
celery_override = override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                                    CELERY_ALWAYS_EAGER=True,
                                    BROKER_URL="memory://",
                                    BROKER_BACKEND="memory",
                                    SITE_REDIRECT=False)

# TODO More granular tests

# Subscription tests:
@tag("subscription")
class TestSubscribeEndpoint(TestCase):
    """
    Tests the subscription creation endpoint.
    """
    def setUp(self):
        self.site_config = site_config.site_config("somerville.cornerwise.org")
        self.client = Client(HTTP_ACCEPT="application/json",
                             HTTP_HOST="somerville.cornerwise.org")
        self.subscribe_url = reverse("subscribe")

    @celery_override
    def test_invalid_query(self):
        data = {"email": "invalid_query@example.com",
                "query": json.dumps({"center": "hello,world"})}
        response = self.client.post(reverse("subscribe"), data)

        self.assertEqual(response.status_code, 401)

    @celery_override
    def test_existing_user(self):
        """When someone attempts to create a new subscription for an email address
        that is already registered:

        """
        data = {"email": "olduser@example.com",
                "query": json.dumps(add_radius({}))}
        response = self.client.post(self.subscribe_url, data)
        response_data = response.json()

        self.assertEqual(response.status_code, 200, response_data)

        self.assertTrue(response_data["new_user"])

        data2 = {"email": "olduser@example.com",
                 "query": json.dumps(add_radius({}))}
        response2 = self.client.post(self.subscribe_url, data2)
        response_data2 = response2.json()

        self.assertEqual(response2.status_code, 200, response_data2)

        self.assertFalse(response_data2["new_user"])

    @tag("site_config", "mail")
    @celery_override
    def test_creation(self):
        """When a new user is created, verify that the server responds correctly and
        that an email is sent. Check that the email contains a valid
        confirmation link.

        """
        data = {"email": "newuser@example.com",
                "query": json.dumps(add_radius({})),
                "language": "en-US"}
        response = self.client.post(self.subscribe_url, data)
        response_data = response.json()

        self.assertEqual(response.status_code, 200, response_data)

        self.assertTrue(response_data["new_user"])
        self.assertFalse(response_data["active"])

        self.assertEqual(len(mail.outbox), 1)
        message: mail.EmailMultiAlternatives = mail.outbox[0]
        self.assertTrue("confirm" in message.subject.lower())

        subs = getattr(message, "substitutions", None)
        if subs and isinstance(subs, dict):
            body = subs["-message_html-"]
        else:
            body = message.message()
            raise Exception("")

        for url in get_links(body):
            if "confirm" in url:
                confirm_url = url
                break
        else:
            self.fail("Did not find a confirmation URL")

        parts = urlsplit(confirm_url)
        params = parse_qs(parts.query)

        try:
            sub = Subscription.objects.get(pk=params["sub"][0])
        except Subscription.DoesNotExist:
            self.fail("Subscription was not created")

        self.assertIsNone(sub.active)
        self.assertFalse(sub.user.is_active)

        response = self.client.get(confirm_url)
        sub = Subscription.objects.get(pk=params["sub"][0])
        self.assertIsNotNone(sub.active)
        self.assertTrue(sub.user.is_active)


@tag("subscription", "site_config")
class TestSubscribe(TestCase):
    def test_site_restrictions(self):
        """
        Check that site-specific constraints are checked.
        """
        subscription = models.Subscription(
            site_name="somerville.cornerwise.gov")
        query = add_radius({})
        query["r"] = D(ft=10000).m

        with self.assertRaises(ValidationError):
            subscription.set_validated_query(query)

        with self.assertRaises(ValidationError):
            subscription.set_validated_query(add_box({}))

        query["r"] = "300m"
        query["region_name"] = "Tunguska, Krasnoyarsk Krai"

        with self.assertRaises(ValidationError):
            subscription.set_validated_query(query)


@tag("inbound", "mail")
class TestInboundParser(TestCase):
    def test_key(self):
        client = Client()
        response = client.post(reverse(mail_parse_views.mail_inbound))
        self.assertEqual(response.status_code, 403)



@tag("user", "authentication", "mail")
class TestUserAuthentication(TestCase):
    @celery_override
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            is_active=True,
            username="auth_test_user",
            email="auth_test_user@example.com")
        self.site_config = site_config.site_config("somerville.cornerwise.org")
        self.profile = UserProfile.objects.create(
            user=self.user,
            site_name=self.site_config.hostname)

    @celery_override
    def test_manager_link(self):
        self.client.post(reverse("resend-confirmation"),
                         {"email": self.user.email})
        message = mail.outbox[0]
        body = message.substitutions["-message_html-"]
        for url in get_links(body):
            if "manage" in url:
                manage_url = url
                break
        else:
            self.fail("Did not find a manager link")

        response = self.client.get(manage_url)
        self.assertEqual(response.status_code, 302)

        manage_url = response["Location"]
        print("redirected to", manage_url)
        response = self.client.get(manage_url)
        self.assertEqual(response.status_code, 200)

    def test_token_invalidation(self):
        """Test that a user authentication token can only be used once.
        """
        pass


@tag("comment", "mail")
class TestUserComments(TestCase):
    def setUp(self):
        self.client = Client(REMOTE_HOST="1234-fake-street.globonet.com",
                             REMOTE_ADDR="123.1.1.1")
        self.admin = User.objects.create(is_active=True,
                                         username="admin",
                                         email="fakeadmin@example.com",
                                         is_superuser=True)

    @celery_override
    def test_send_comment(self):
        data = {
            "send_to": "cornerwise",
            "subject": "Hello",
            "comment": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        }
        response = self.client.post(reverse("contact-us"), data)

        self.assertEqual(response.status_code, 200)

        comment = models.UserComment.objects.order_by("-created")[0]
        self.assertEqual(comment.subject, data["subject"])
        self.assertEqual(comment.comment, data["comment"])

        self.assertEqual(len(mail.outbox), 1)
        message: mail.EmailMessage = mail.outbox[0]

        self.assertIn(self.admin.email, message.recipients())

        html = message.substitutions["-message_html-"]
        self.assertIn("Hello", html)

    @celery_override
    def test_invalid_comment(self):
        data = {
            "send_to": "123123ASDA!!",
            "subject": "",
            "comment": ""
        }
        response = self.client.post(reverse("contact-us"), data)
        self.assertEqual(response.status_code, 400)

        json = response.json()
        self.assertIn("errors", json)
        self.assertIn("send_to", json["errors"])
        self.assertIn("comment", json["errors"])


@tag("notifications")
class TestAdminNotifications(TestCase):
    def setUp(self):
        # Create some subs
        pass

    def test_notifications_sent(self):
        """
        """
        pass



@tag("changesets")
class TestChangeSetCreation(TestCase):
    def setUp(self):
        pass

    def test_combine_changesets(self):
        changeset_1 = {
            "changes": {
                1: {}
            }
        }
        pass

## Create from valid queries

## Test that Subscription creates a new user.

## Test that a welcome email is sent

## Test that the link in the email is correct

## Test that Subscriptions nearby are correctly found:
### For region subscriptions
### For center/radius subscriptions

## Test that changes are correctly calculated
## Test combining changesets
