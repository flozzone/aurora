from django.contrib import admin
from ObjectState.models import ObjectState

class ObjectStateAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'content_type',
                    'object_id',
                    'expired',
                ]
            }
        ),
    ]
    list_display = ('id', 'content_type', 'object_id', 'expired', )

admin.site.register(ObjectState, ObjectStateAdmin)