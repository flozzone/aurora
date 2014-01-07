import os
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from PortfolioUser.models import PortfolioUser
from FileUpload.models import UploadFile


@login_required()
def file_upload(request):
    user = PortfolioUser.objects.get(id=request.user.id)
    if 'elaboration_id' in request.POST:
        print(request.POST)
        elaboration_id = request.POST.get('elaboration_id')
        upload_file = UploadFile(user=user, elaboration_id=elaboration_id, upload_file=request.FILES['file'])
        upload_file.save()
    return HttpResponse(upload_file.upload_file.name)


@login_required()
def file_remove(request):
    user = PortfolioUser.objects.get(id=request.user.id)
    if 'url' in request.GET:
        url = request.GET.get('url')
        files = UploadFile.objects.filter(user=user)
        for file in files:
            if file.upload_file.name == url:
                file.delete()
    return HttpResponse("OK")


@login_required()
def all_files(request):
    user = PortfolioUser.objects.get(id=request.user.id)
    if 'elaboration_id' in request.GET:
        elaboration_id = request.GET.get('elaboration_id')
        data = []
        for upload_file in UploadFile.objects.filter(user=user, elaboration__id=elaboration_id):
            data.append({
                'name': os.path.basename(upload_file.upload_file.name),
                'size': upload_file.upload_file.size,
                'path': upload_file.upload_file.name,
            })
    return HttpResponse(json.dumps(data))