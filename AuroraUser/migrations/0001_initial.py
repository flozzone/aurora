# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import AuroraUser.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('Course', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuroraUser',
            fields=[
                ('user_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to=settings.AUTH_USER_MODEL, serialize=False)),
                ('nickname', models.CharField(null=True, blank=True, max_length=100)),
                ('last_activity', models.DateTimeField(auto_now_add=True)),
                ('statement', models.TextField(blank=True)),
                ('avatar', models.ImageField(null=True, upload_to=AuroraUser.models.avatar_path, blank=True)),
                ('matriculation_number', models.CharField(unique=True, null=True, blank=True, max_length=100)),
                ('study_code', models.CharField(null=True, default='', blank=True, max_length=100)),
                ('oid', models.CharField(unique=True, null=True, blank=True, max_length=30)),
                ('last_selected_course', models.ForeignKey(to='Course.Course', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'user',
                'abstract': False,
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
        ),
    ]
