import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


def get_upload_path(instance, filename):
    name = "no_elaboration"
    if instance.elaboration:
        name = filename
    return os.path.join(
        "upload",
        str(instance.user.id),
        name
    )


class UploadFile(models.Model):
    user = models.ForeignKey('AuroraUser.AuroraUser')
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    creation_time = models.DateTimeField(auto_now_add=True)
    upload_file = models.FileField(upload_to=get_upload_path)


@receiver(post_delete, sender=UploadFile)
def upload_file_post_delete_handler(sender, **kwargs):
    upload_file = kwargs['instance']
    storage, path = upload_file.upload_file.storage, upload_file.upload_file.path
    storage.delete(path)