from django.contrib.gis.db import models

from base64 import b64encode
import pickle
import random


def make_token():
    return b64encode(random.getrandbits(256).to_bytes(32, "big"))


class User(models.Model):
    email = models.EmailField()
    # Used for managing preferences
    token = models.CharField(max_length=64, default=make_token)
    # The user should not be able to log in if this is false:
    activated = models.BooleanField(default=False)

    def generate_token(self):
        self.token = make_token()
        self.save()


class Subscription(models.Model):
    # The subscription belong to a registered user:
    user = models.ForeignKey(User, null=True,
                             related_name="subscriptions")
    email = models.EmailField()
    # Stores the pickle serialization of a dictionary describing the query
    query = models.BinaryField()
    last_notified = models.DateTimeField(auto_now=True)
    # This code can be used to add or remove the subscription
    subscription_key = models.CharField(null=True)
    # This becomes True once the user has verified the subscription
    active = models.BooleanField(default=False, db_index=True)


    @property
    def query_dict(self):
        return pickle.loads(self.query)

    @query_dict.setter
    def query_dict(self, new_dict):
        self.query = pickle.dumps(new_dict)
