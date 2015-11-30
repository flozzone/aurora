import os
import hashlib
import re
from taggit.managers import TaggableManager
from urllib.parse import urlparse
import urllib.request
from django.db import models
from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes.models import ContentType
from AuroraProject.settings import STATIC_ROOT, MEDIA_ROOT
from Elaboration.models import Elaboration
from django.core.files import File

def avatar_path(instance, filename):
    name = 'avatar_%s' % instance.id
    fullname = os.path.join(instance.upload_path, name)
    if os.path.exists(fullname):
        os.remove(fullname)
    return fullname

class AuroraUser(User):
    nickname = models.CharField(max_length=100, null=True, blank=True)
    last_activity = models.DateTimeField(auto_now_add=True, blank=True)
    statement = models.TextField(blank=True)
    upload_path = 'avatar'
    avatar = models.ImageField(upload_to=avatar_path, null=True, blank=True)
    matriculation_number = models.CharField(max_length=100, null=True, unique=True, blank=True)
    study_code = models.CharField(max_length=100, null=True, blank=True, default="")
    oid = models.CharField(max_length=30, null=True, unique=True, blank=True)
    tags = TaggableManager()

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def get_elaborations(self):
        elaborations = []
        for elaboration in Elaboration.objects.filter(user=self, submission_time__isnull=False):
            elaborations.append(elaboration)
        return elaborations

    def get_course_elaborations(self, course):
        elaborations = []
        for elaboration in Elaboration.objects.filter(user=self, challenge__course=course, submission_time__isnull=False):
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

    def get_content_type_id(self):
        return ContentType.objects.get_for_model(self).id

    def add_tags_from_text(self, text):
        tags = text.split(',');
        tags = [tag.lower().strip() for tag in tags]
        self.tags.add(*tags)

    def remove_tag(self, tag):
        self.tags.remove(tag)

    @staticmethod
    def query_tagged(tags):
        return AuroraUser.objects.filter(tags__name__in=tags)

    @property
    def display_name(self):
        display_name = self.username if self.nickname is None else self.nickname
        return display_name
