import os
from django import template

from Elaboration.models import Elaboration
from FileUpload.models import UploadFile


register = template.Library()


@register.inclusion_tag('elaboration_files.html', takes_context=True)
def render_uploads(context, elaboration):
    elaboration = Elaboration.objects.get(id=elaboration.id)
    files = []
    index = 0
    for upload_file in UploadFile.objects.filter(user=elaboration.user, elaboration__id=elaboration.id).order_by(
            'creation_time'):
        index += 1
        figure = 'Fig. ' + str(index)

        file_map = {'name': os.path.basename(upload_file.upload_file.name),
                    'size': round((upload_file.upload_file.size / 1048576), 2),
                    'url': upload_file.upload_file.url,
                    'thumbnail_url': upload_file.thumbnail.url,
                    'accepted_files': elaboration.challenge.accepted_files}
        if 'pdf' not in elaboration.challenge.accepted_files:
            file_map['fig'] = figure
        files.append(file_map)
    context.update({'files': files})
    return context