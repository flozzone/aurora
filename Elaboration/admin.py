from django.contrib import admin
from django.http import HttpResponse
from Elaboration.models import *

def export_csv(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=elaboration.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))
    writer.writerow([
        smart_str(u"id"),
        smart_str(u"challenge"),
        smart_str(u"user"),
        smart_str(u"creation_time"),
        smart_str(u"submission_time"),
    ])
    for obj in modeladmin.model.objects.all():
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.challenge),
            smart_str(obj.user),
            smart_str(obj.creation_time),
            smart_str(obj.submission_time),
        ])
    return response
export_csv.short_description = u"Export CSV"

class ElaborationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'challenge',
                    'user',
                    'creation_time',
                    'elaboration_text',
                    'submission_time',
                    'tags',
                ]
            }
        ),
    ]
    list_display = ('id', 'challenge', 'user', 'creation_time', 'elaboration_text', 'submission_time', )
    search_fields = ('user__username','challenge__id',)
    readonly_fields = ("creation_time",)
    actions = [export_csv]

admin.site.register(Elaboration, ElaborationAdmin)