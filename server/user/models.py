from django.contrib.auth.models import User
from django.contrib.gis.db import models

import pickle


class Subscription(models.Model):
    # The subscription belong to a registered user:
    user = models.ForeignKey(User, null=True)
    email = models.EmailField()
    # Stores the pickle serialization of a dictionary describing the query
    query = models.BinaryField()
    last_notified = models.DateTimeField(auto_now=True)

    @property
    def query_dict(self):
        return pickle.loads(self.query)

    @query_dict.setter
    def query_dict(self, new_dict):
        self.query = pickle.dumps(new_dict)
