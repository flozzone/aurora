import sys
import urllib, hashlib
from django.db import models
from django.contrib.auth.models import User, UserManager
from Elaboration.models import Elaboration


class PortfolioUser(User):
    nickname = models.CharField(max_length=100, null=True, blank=True)
    statement = models.TextField()
    last_activity = models.DateTimeField(auto_now_add=True, blank=True)
    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def get_elaborations(self):
        elaborations = []
        for elaboration in Elaboration.objects.filter(user=self):
            elaborations.append(elaboration)
        return elaborations

    def get_gravatarurl(self):
        gravatarurl = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower().encode("utf-8")).hexdigest() + "?"
        gravatarurl += urllib.parse.urlencode({'d':'identicon', 's':str(30)})
        return gravatarurl
