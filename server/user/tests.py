from django.test import Client, TestCase, tag, override_settings
from django.urls import reverse
from django.conf import settings
from django.core import mail
from django.core.exceptions import ValidationError

from django.contrib.auth import authenticate, get_user_model
from django.contrib.gis.measure import D

import json
import random
from urllib.parse import parse_qs, urlsplit

from . import models, views, mail_parse_views
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


# Decorator to override celery settings during tests
celery_override = override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                                    CELERY_ALWAYS_EAGER=True,
                                    BROKER_URL="memory://",
                                    BROKER_BACKEND="memory")

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


    @tag("site_config")
    @celery_override
    def test_creation(self):
        """When a new user is created, verify that the server responds correctly and
        that an email is sent. Check that the email contains a valid link.

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
        self.assertTrue("welcome" in message.subject.lower())

        subs = getattr(message, "substitutions")
        self.assertIsInstance(subs, dict)
        print(subs)
        confirm_url = message.substitutions["-confirm_url-"]
        parts = urlsplit(confirm_url)
        self.assertEqual(parts.hostname, self.site_config.hostname)

        params = parse_qs(parts.query)
        uid = params["uid"][0]
        user = authenticate(pk=uid, token=params["token"][0])
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

        # Check that confirmation works
        response = self.client.get(f"{parts.path}?{parts.query}")


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

        query["r"] = D(ft=300).m
        query["region_name"] = "Tunguska, Krasnoyarsk Krai"

        with self.assertRaises(ValidationError):
            subscription.set_validated_query(query)


@tag("inbound", "mail")
class TestInboundParser(TestCase):
    def test_key(self):
        client = Client()
        response = client.post(reverse(mail_parse_views.mail_inbound))
        self.assertEqual(response.status_code, 403)


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

        recipient = message.recipients()[0]
        self.assertEqual(recipient, self.admin.email)



@tag("notifications")
class TestAdminNotifications(TestCase):
    def setUp(self):
        # Create some subs
        pass

    def test_notifications_sent(self):
        """
        """
        pass

## Create from valid queries

## Test that Subscription creates a new user.

## Test that a welcome email is sent

## Test that the link in the email is correct

## Test that Subscriptions nearby are correctly found:
### For region subscriptions
### For center/radius subscriptions

## Test that changes are correctly calculated
