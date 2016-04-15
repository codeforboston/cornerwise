from django.contrib.gis.db import models
from django.core.urlresolvers import reverse

from utils import prettify_lat, prettify_long

from base64 import b64encode
import pickle
import random
import re


def make_token():
    return b64encode(random.getrandbits(256).to_bytes(32, "big"))


class User(models.Model):
    email = models.EmailField(unique=True)
    # Used for managing preferences
    token = models.CharField(max_length=64, default=make_token)
    # The user should not be able to log in if this is false:
    activated = models.BooleanField(default=False)
    nickname = models.CharField(max_length=128, empty=True,
                                help="What do you prefer to be called?")

    def activate(self):
        self.activated = True
        self.token = make_token()
        self.save()

    def generate_token(self):
        "Creates a new verification token for the user and saves it."
        self.token = make_token()
        self.save()

        return self.token

    def confirmation_link(self):
        return reverse("confirm-user",
                       kwargs={"token": self.token,
                               "pk": self.pk})


class Subscription(models.Model):
    # The subscription belong to a registered user:
    user = models.ForeignKey(User, null=True,
                             related_name="subscriptions")
    # Stores the pickle serialization of a dictionary describing the query
    query = models.BinaryField()
    last_notified = models.DateTimeField(auto_now=True)

    @property
    def query_dict(self):
        return pickle.loads(self.query)

    @query_dict.setter
    def query_dict(self, new_dict):
        self.query = pickle.dumps(new_dict)

    def set_validated_query(self, q):
        self.query_dict = self.validate_query(q)

    valid_keys = {
        "projects": lambda v: v.lower() in {"all", "null"},
        "text": lambda _: True,
        "box": lambda v: (len(v.split(",")) == 4 and
                          all(re.match(r"-?\d+\.\d+", c)
                              for c in v.split(",")))
    }

    @classmethod
    def validate_query(kls, q):
        validated = {}
        for k, v in q.items():
            if k not in kls.valid_keys:
                continue

            if kls.valid_keys[k](v):
                validated[k] = v

        return validated

    @staticmethod
    def readable_query(query):
        if "project" in query:
            if query["project"] == "all":
                desc = "Public proposals "
            else:
                desc = "Private proposals "
        else:
            desc = "All proposals "

        if "text" in query:
            desc += "matching \"" + query["text"] + "\" "

        if "box" in query:
            coords = [float(s) for s in query["box"].split(",")]
            desc += "".join(["between ", prettify_lat(coords[0]), ", ",
                             prettify_long(coords[1]), " and ",
                             prettify_lat(coords[2]), ", ",
                             prettify_long(coords[3])])

        return desc

    def readable_description(self):
        return self.readable_query(self.query_dict)
