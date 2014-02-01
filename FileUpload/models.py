from django.db import models
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver


def get_upload_path(instance, filename):
    return os.path.join("static", "upload", str(instance.user.id), str(UploadFile.objects.all().count()) + '_' + filename)


class UploadFile(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    creation_time = models.DateTimeField(auto_now_add=True)
    upload_file = models.FileField(upload_to=get_upload_path)

@receiver(post_delete, sender=UploadFile)
def upload_file_post_delete_handler(sender, **kwargs):
    upload_file = kwargs['instance']
    storage, path = upload_file.upload_file.storage, upload_file.upload_file.path
    storage.delete(path)