import os
from django import template
from AuroraUser.models import AuroraUser

register = template.Library()

@register.inclusion_tag('tags.html')
def render_tags(user_id):
    user = AuroraUser.objects.get(pk=user_id)
    return {'user': user}
