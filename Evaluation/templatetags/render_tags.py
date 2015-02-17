import os
from django import template
from AuroraUser.models import AuroraUser

register = template.Library()

@register.inclusion_tag('tags.html', takes_context=True)
def render_tags(context, user_id):
    user = AuroraUser.objects.get(pk=user_id)
    context.update({'user': user})
    return context
