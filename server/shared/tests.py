from django.test import Client, TestCase, tag, override_settings

from django.contrib.auth import get_user_model

from user.models import Subscription, UserProfile

from .geocoder import Geocoder
from .staff_notifications import UserNotificationForm
import utils


import warnings
warnings.filterwarnings(
    'ignore', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields')

User = get_user_model()

celery_override = override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                                    CELERY_ALWAYS_EAGER=True,
                                    BROKER_URL="memory://",
                                    BROKER_BACKEND="memory")

class StaffNotificationTest(TestCase):
    @classmethod
    def setUpClass(kls):
        addr = "93 Highland Ave, Somerville, MA 02143"
        geocoded = Geocoder.geocode([addr])[0]
        location = geocoded["location"]

        user = User.objects.create(is_active=False,
                                   username="testuser@example.com",
                                   email="testuser@example.com")
        profile = UserProfile.objects.create(user=user)

        sub = Subscription()
        sub.set_validated_query({
            "center": "{d[lat]},{d[lng]}".format(d=location),
            "r": "90"
        })
        sub.user = User

        kls.addr = addr
        kls.sub = sub
        kls.user = user

    def setUp(self):
        self.client = Client(HTTP_HOST="somerville.cornerwise.org")

    @tag("admin")
    def test_notifications(self):
        form = UserNotificationForm({
            "addresses": self.addr,
            "title": "Alert: Rampaging megafauna",
            "message": "A chaos of mini-Godzillas has overrun Davis Square. Please remain indoors. They are 'mini' only relative to Godzilla, who, we remind you, was as large as a skyscraper. So they're still quite large.",
            "confirm": "1"
        })
        self.assertTrue(form.is_valid())


@tag("utils")
class UtilitiesTests(TestCase):
    def test_absolute_url(self):
        with override_settings(BASE_URL=None, SERVER_DOMAIN="cornerwise.org"):
            self.assertEqual(utils.make_absolute_url("/hello"),
                             "https://cornerwise.org/hello")
            self.assertEqual(utils.make_absolute_url("http://google.com"),
                             "http://google.com")
        with override_settings(BASE_URL="http://localhost:4000"):
            self.assertTrue(
                utils.make_absolute_url("/hello",
                                        "somervillema.cornerwise.org")\
                .startswith("http://localhost:4000/hello"))
            self.assertEqual(utils.make_absolute_url("http://google.com"),
                             "http://google.com")
