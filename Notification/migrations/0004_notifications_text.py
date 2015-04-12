import os
from django.db import migrations, models

from AuroraProject.settings import STATIC_URL


class Migration(migrations.Migration):
    dependencies = [("AuroraUser", "0003_aurorauser_tags")]

    operations = [
        migrations.AlterField('notifications', 'text', models.TextField()),
        migrations.AlterField('notifications', 'image_url',
                              models.TextField(default=os.path.join(STATIC_URL, 'img', 'info.jpg'))),
        migrations.AlterField('notifications', 'link', models.TextField(default="")),
    ]