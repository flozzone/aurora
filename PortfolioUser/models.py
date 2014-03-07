import os
import hashlib
from urllib.parse import urlparse
import urllib.request
from django.db import models
from django.contrib.auth.models import User, UserManager
from AmanamanProjekt.settings import STATIC_ROOT, MEDIA_ROOT
from Elaboration.models import Elaboration
from django.core.files import File

def avatar_path(instance, filename):
    name = 'avatar_%s' % instance.id
    fullname = os.path.join(instance.upload_path, name)
    if os.path.exists(fullname):
        os.remove(fullname)
    return fullname

class PortfolioUser(User):
    nickname = models.CharField(max_length=100, null=True, blank=True)
    last_activity = models.DateTimeField(auto_now_add=True, blank=True)
    statement = models.TextField()
    upload_path = 'avatar'
    avatar = models.ImageField(upload_to=avatar_path, null=True, blank=True)
    matriculation_number = models.CharField(max_length=100, null=True)
    study_code = models.CharField(max_length=100, null=True, blank=True, default="")
    last_selected_course = models.ForeignKey('Course.Course', null=True)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def get_elaborations(self):
        elaborations = []
        for elaboration in Elaboration.objects.filter(user=self):
            elaborations.append(elaboration)
        return elaborations

    def get_challenge_elaboration(self, challenge):
        return challenge.get_elaboration(self)

    def get_stack_elaborations(self, stack):
        elaborations = []
        for challenge in stack.get_challenges():
            elaboration = self.get_challenge_elaboration(challenge)
            if elaboration and elaboration.is_submitted():
                elaborations.append(elaboration)
        return elaborations

    def get_gravatar(self):
        filename = "avatar_" + str(self.id)
        if not os.path.isdir(os.path.join(MEDIA_ROOT,self.upload_path)):
            os.makedirs(os.path.join(MEDIA_ROOT,self.upload_path))
        try:
            print("\a")
            gravatarurl = "http://www.gravatar.com/avatar/" + hashlib.md5(
                self.email.lower().encode("utf-8")).hexdigest() + "?"
            gravatarurl += urllib.parse.urlencode({'d': 'monsterid', 's': str(192)})
            result = urllib.request.urlretrieve(gravatarurl)
            self.avatar.save(avatar_path(self, ''), File(open(result[0], 'rb')))
        except IOError:
            from shutil import copyfile
            copyfile(os.path.join(STATIC_ROOT, 'img', 'default_gravatar.png'), os.path.join(self.upload_path, filename))
        self.avatar = os.path.join(self.upload_path, filename)
        self.save()

    @property
    def display_name(self):
        display_name = self.username if self.nickname is None else self.nickname
        return display_name
