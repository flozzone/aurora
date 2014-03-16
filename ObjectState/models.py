from django.db import models as models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class ObjectState(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    expired = models.BooleanField(default=False)

    @staticmethod
    def set_expired(ref_object, state):
        ref_type = ContentType.objects.get_for_model(ref_object)

        try:
            obj = ObjectState.objects.get(
                content_type__pk=ref_type.id,
                object_id=ref_object.id)
        except ObjectState.DoesNotExist:
            obj = ObjectState.objects.create(content_object=ref_object)

        obj.expired = not obj.expired
        obj.save()
        return True

    @staticmethod
    def get_expired(ref_object):
        ref_type = ContentType.objects.get_for_model(ref_object)

        try:
            obj = ObjectState.objects.get(
                content_type__pk=ref_type.id,
                object_id=ref_object.id)
            return obj.expired
        except ObjectState.DoesNotExist:
            return False