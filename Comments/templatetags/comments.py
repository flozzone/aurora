from django import template

register = template.Library()

# {% get_comment_list for [object] as [varname] %}
# {% render_comment_list for [object] %}