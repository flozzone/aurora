from django.shortcuts import render, render_to_response
from django.template import RequestContext
from FileUpload.forms import UploadFileForm
import json
from django.contrib.auth.decorators import login_required
from PortfolioUser.models import PortfolioUser
from Review.models import Review
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from django.http import HttpResponse
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from FileUpload.models import UploadFile

@login_required()
def file_upload(request):
    user = PortfolioUser.objects.get(id=request.user.id)
    upload_file = UploadFile(user=user, upload_file=request.FILES['file'])
    upload_file.save()
    for upload_file in UploadFile.objects.all():
        print(upload_file.id)
        print(upload_file.upload_file.name)
    return HttpResponse("Test")