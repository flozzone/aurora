from django.contrib import admin
from Slides.models import Slide
from Slides.models import Lecture

admin.site.register(Slide)
admin.site.register(Lecture)