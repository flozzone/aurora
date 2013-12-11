from django import template
from django.contrib.contenttypes.models import ContentType
from Comments.models import Comment
from django.template.loader import render_to_string

register = template.Library()

# {% get_comment_list for [object] as [varname] %}
# {% render_comment_list for [object] %}


class CommentListNode(template.Node):
    def __init__(self, reference):
        self.reference_var = template.Variable(reference)

    def render(self, context):
        try:
            reference = self.reference_var.resolve(context)

            ref_type = ContentType.objects.get_for_model(reference)
            queryset = Comment.objects.filter(
                parent=None,
                content_type__pk=ref_type.id,
                object_id=reference.id).order_by('-post_date')

            print("tag queryset")
            print(queryset)

            context = {'comment_list': queryset}

            rendered = render_to_string('Comments/comment_list.html', context)
            return rendered
        except template.VariableDoesNotExist:
            return ''


@register.tag
#def render_comment_list_plain_tag(parser, token):
def render_comment_list(parser, token):
    tokens = token.split_contents()
    usage = 'template tag has to look like this: {% ' \
            + tokens[0] + ' for <reference> %}'

    if len(tokens) != 3:
        raise template.TemplateSyntaxError(usage)

    if tokens[1] != 'for':
        raise template.TemplateSyntaxError(usage)

    return CommentListNode(tokens[2])


def get_reference_type_pk(ref_object):
    object_type = ContentType.objects.get_for_model(ref_object)
    object_pk = ref_object.id
    return object_type, object_pk

    #Comments.objects.filter(content_type__pk=object_type.id, object_id=ref_object.id)

@register.inclusion_tag('Comments/comment_list.html')
def render_comment_list_inclusion_tag(for_string, reference):
    # TODO create model from reference object
    # TODO lookup comments associated with reference object model and create context (i.e. a comment_list)
    from Comments.views import CommentForm
    from Comments.views import CommentList
    from Comments.models import Comment

    print('first the for:')
    print(for_string)
    print('then the reference type')
    print(type(reference))
    print(reference)

    usage = 'template tag has to look like this: {% ' \
            + render_comment_list.__name__ + ' for <reference> %}'

    if for_string != 'for':
        raise template.TemplateSyntaxError(usage)

    ref_type = ContentType.objects.get_for_model(reference)

    queryset = Comment.objects.filter(parent=None, content_type__pk=ref_type.id, object_id=reference.id).order_by('-post_date')
    context = {'comment_list': queryset}
    #           'form': CommentForm()}

    #context = CommentList().get_context_data()
    #context = {'test_var': reference}

    #bookmark_type = ContentType.objects.get_for_model(b)
    #TaggedItem.objects.filter(content_type__pk=bookmark_type.id, object_id=b.id)
    return context