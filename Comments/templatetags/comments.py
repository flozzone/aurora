from django import template

register = template.Library()

# {% get_comment_list for [object] as [varname] %}
# {% render_comment_list for [object] %}


class CommentListNode(template.Node):
    def __init__(self, reference):
        self.reference = template.Variable(reference)

    def render(self, context):
        try:
            return "funky shit: " + self.reference.resolve(context)
        except template.VariableDoesNotExist:
            return ''


@register.tag
def render_comment_list(parser, token):
    tokens = token.split_contents()
    usage = 'template tag has to look like this: {% ' \
            + tokens[0] + ' for <reference> %}'

    if len(tokens) != 3:
        raise template.TemplateSyntaxError(usage)

    if tokens[1] != 'for':
        raise template.TemplateSyntaxError(usage)

    return CommentListNode(tokens[2])