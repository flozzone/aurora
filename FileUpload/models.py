from django.db import models
import os


def get_upload_path(instance, filename):
    return os.path.join("upload", str(instance.user.id), str(UploadFile.objects.all().count()) + '_' + filename)


class UploadFile(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creation_time = models.DateTimeField(auto_now_add=True)
    upload_file = models.FileField(upload_to=get_upload_path)

