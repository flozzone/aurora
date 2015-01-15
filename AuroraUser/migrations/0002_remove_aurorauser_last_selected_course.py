# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AuroraUser', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aurorauser',
            name='last_selected_course',
        ),
    ]
