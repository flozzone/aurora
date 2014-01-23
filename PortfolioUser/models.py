import os
import hashlib
from urllib.parse import urlparse
import urllib.request
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User, UserManager
from Elaboration.models import Elaboration


class PortfolioUser(User):
    nickname = models.CharField(max_length=100, null=True, blank=True)
    statement = models.TextField()
    last_activity = models.DateTimeField(auto_now_add=True, blank=True)
    upload_path = 'static/img'
    avatar = models.ImageField(upload_to=upload_path, null=True, blank=True)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def get_elaborations(self):
        elaborations = []
        for elaboration in Elaboration.objects.filter(user=self):
            elaborations.append(elaboration)
        return elaborations

    def get_challenge_elaboration(self, challenge):
        try:
            elaboration = Elaboration.objects.get(user=self, challenge=challenge)
        except Elaboration.DoesNotExist:
            elaboration = None
        return elaboration

    def get_stack_elaborations(self, stack):
        elaborations = []
        for challenge in stack.get_challenges():
            if self.get_challenge_elaboration(challenge):
                elaborations.append(self.get_challenge_elaboration(challenge))
        return elaborations

    def get_gravatar(self):
        gravatarurl = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower().encode("utf-8")).hexdigest() + "?"
        gravatarurl += urllib.parse.urlencode({'d':'monsterid', 's':str(30)})

        filename = "avatar_" + self.username + str(self.id) + ".jpg"
        urllib.request.urlretrieve(gravatarurl, os.path.join(self.upload_path, filename))
        self.avatar = os.path.join(self.upload_path, filename)
        self.save()

    @property
    def display_name(self):
        display_name = self.username if self.nickname is None else self.nickname
        return display_name
