import os
from django import template
from django.http import request
from Elaboration.models import Elaboration
from FileUpload.models import UploadFile

register = template.Library()

@register.inclusion_tag('uploads.html')
def render_uploads(elaboration):
    elaboration = Elaboration.objects.get(id=elaboration.id)
    files = []
    for upload_file in UploadFile.objects.filter(user=elaboration.user, elaboration__id=elaboration.id):
        files.append([os.path.basename(upload_file.upload_file.name),
                      upload_file.upload_file.size,
                      upload_file.upload_file.url])

    return {'files' : files}