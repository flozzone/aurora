import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.core.files import File
from tempfile import NamedTemporaryFile
from PIL import ImageFile, Image, ImageOps
from Elaboration.models import Elaboration
from FileUpload.models import UploadFile
from django.http import Http404
from django.conf import settings

@login_required()
def file_upload(request):
    user = RequestContext(request)['user']
    file = request.FILES['file']
    if 'elaboration_id' in request.POST:
        elaboration_id = request.POST.get('elaboration_id')
        try:
            elaboration = Elaboration.objects.get(pk=elaboration_id)
            if not elaboration.user == user:
                return file_upload_failed_response()
            upload_file = UploadFile(user=user, elaboration_id=elaboration_id, upload_file=file)
        except Exception as e:
            return file_upload_failed_response(str(e))
        if file.name.endswith('.pdf'):
            with open(settings.STATIC_ROOT + '/img/pdf_icon.jpg', 'rb') as pdf_icon:
                create_thumbnail(File(pdf_icon), file.name, upload_file.thumbnail.save)
        else:
            try:
                create_thumbnail(file, file.name, upload_file.thumbnail.save)
            except Exception:
                with open(settings.STATIC_ROOT + '/img/info.jpg', 'rb') as pdf_icon:
                    create_thumbnail(File(pdf_icon), file.name, upload_file.thumbnail.save)
        upload_file.save()
    elif 'user_id' in request.POST:
        if not request.POST.get('user_id') == str(user.id):
            raise Http404
        filename = 'avatar_' + str(user.id)
        create_thumbnail(file, filename, user.avatar.save)
        user.save()
        return HttpResponse(user.avatar.name)
    response = {'id': upload_file.id, 'url': upload_file.upload_file.url, 'thumbnail_url': upload_file.thumbnail.url}
    return HttpResponse(json.dumps(response))

def create_thumbnail(file, filename, save_function):
    parser = ImageFile.Parser()
    while 1:
        chunk = file.read(1024)
        if not chunk:
            break
        parser.feed(chunk)
    image = parser.close()
    size = (120, 120)
    image = ImageOps.fit(image, size, Image.ANTIALIAS, centering=(0.5, 0.5))
    with NamedTemporaryFile() as tmp:
        image.save(tmp, 'png')
        tmp_file = File(tmp)
        tmp_file.path = filename
        save_function(filename, tmp_file, False)


@login_required()
def file_remove(request):
    user = RequestContext(request)['user']
    if 'id' in request.GET:
        id = request.GET.get('id')
        file = UploadFile.objects.get(pk=id)
        if file.user.id == user.id:
            file.delete()
        else:
            raise Http404
    return HttpResponse("OK")


@login_required()
def all_files(request):
    print("requesting all files")
    user = RequestContext(request)['user']
    if 'elaboration_id' in request.GET:
        elaboration_id = request.GET.get('elaboration_id')
        try:
            elaboration = Elaboration.objects.get(pk=elaboration_id)
            if not elaboration.user == user:
                raise Http404
        except:
            raise Http404
        data = []
        for upload_file in UploadFile.objects.filter(user=elaboration.user, elaboration__id=elaboration_id).order_by('creation_time'):
            data.append({
                'name': os.path.basename(upload_file.upload_file.name),
                'size': upload_file.upload_file.size,
                'url': upload_file.upload_file.url,
                'thumbnail_url': upload_file.thumbnail.url,
                'id': upload_file.id,
            })
    return HttpResponse(json.dumps(data))

def file_upload_failed_response(reason):
    print('upload failed')
    response = HttpResponse('File Upload failed:' + reason)
    response.status_code = 500
    print(response.status_code)
    return response