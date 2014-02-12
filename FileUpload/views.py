import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.core.files import File
from io import StringIO
from tempfile import NamedTemporaryFile
from PIL import ImageFile, Image, ImageOps
from Elaboration.models import Elaboration
from FileUpload.models import UploadFile

@login_required()
def file_upload(request):
    user = RequestContext(request)['user']
    if 'elaboration_id' in request.POST:
        elaboration_id = request.POST.get('elaboration_id')
        upload_file = UploadFile(user=user, elaboration_id=elaboration_id, upload_file=request.FILES['file'])
        upload_file.save()
    if 'user_id' in request.POST:
        request.FILES['file'].name = 'avatar_' + str(user.id)
        parser = ImageFile.Parser()
        while 1:
            chunk = request.FILES['file'].read(1024)
            if not chunk:
                break
            parser.feed(chunk)
        image = parser.close()
        THUMBNAIL_SIZE = (192, 192)
        image = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS, centering=(0.5, 0.5))
        with NamedTemporaryFile() as tmp:
            image.save(tmp, 'png')
            tmp_file = File(tmp)
            tmp_file.path = request.FILES['file'].name
            user.avatar.save(request.FILES['file'].name, tmp_file, False)
        user.save()
        return HttpResponse(user.avatar.name)
    return HttpResponse(upload_file.upload_file.name)


@login_required()
def file_remove(request):
    user = RequestContext(request)['user']
    if 'url' in request.GET:
        url = request.GET.get('url')
        files = UploadFile.objects.filter(user=user)
        for file in files:
            if file.upload_file.name == url:
                file.delete()
    return HttpResponse("OK")


@login_required()
def all_files(request):
    if 'elaboration_id' in request.GET:
        elaboration_id = request.GET.get('elaboration_id')
        elaboration = Elaboration.objects.get(id=elaboration_id)
        data = []
        for upload_file in UploadFile.objects.filter(user=elaboration.user, elaboration__id=elaboration_id):
            data.append({
                'name': os.path.basename(upload_file.upload_file.name),
                'size': upload_file.upload_file.size,
                'path': upload_file.upload_file.name,
            })
    return HttpResponse(json.dumps(data))