from django import template

register = template.Library()


@register.inclusion_tag('send_notification_button.html')
def send_notification_button(course_short_title, user_id):
    return {
        'course_short_title': course_short_title,
        'notification_user_id': user_id,
    }
