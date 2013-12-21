from django import template
from django.contrib.contenttypes.models import ContentType
from Comments.models import Comment
from Comments.views import CommentForm
from django.template.loader import render_to_string

register = template.Library()

# {% get_comment_list for [object] as [varname] %} => assignment_tag
# {% render_comment_list for [object] %}


class CommentListNode(template.Node):
    def __init__(self, reference):
        self.reference_var = template.Variable(reference)
        #self.request_var = template.Variable('request')
        #self.request_var = template.Variable('messages')

    def render(self, context):
        print(context)
        #context.push()
        print(context)
        #print(self.request_var.resolve(context))
        #request.path
        try:
            reference = self.reference_var.resolve(context)

            ref_type = ContentType.objects.get_for_model(reference)
            queryset = Comment.objects.filter(
                parent=None,
                content_type__pk=ref_type.id,
                object_id=reference.id).order_by('-post_date')

            form = CommentForm()
            form.fields['reference_id'].initial = reference.id
            form.fields['reference_type_id'].initial = ref_type.id
            context.update({'comment_list': queryset, 'form': form})

            return render_to_string('Comments/comment_list.html', context)
        except template.VariableDoesNotExist:
            return ''


@register.tag
def render_comment_list_plain_tag(parser, token):
#def render_comment_list(parser, token):
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


# TODO delete:
@register.inclusion_tag('Comments/comment_list.html', takes_context=True)
def test_inclusion_tag(context):
    print(context['request'])


@register.inclusion_tag('Comments/comment_list.html')
def render_comment_list(for_string, reference):
    from Comments.views import CommentForm
    from Comments.models import Comment

    #usage = 'template tag has to look like this: {% ' \
    #        + render_comment_list.__name__ + ' for <reference> %}'

    #if for_string != 'for':
    #    raise template.TemplateSyntaxError(usage)

    ref_type = ContentType.objects.get_for_model(reference)

    queryset = Comment.objects.filter(
        parent=None,
        content_type__pk=ref_type.id,
        object_id=reference.id).order_by('-post_date')

    form = CommentForm()
    form.fields['reference_id'].initial = reference.id
    form.fields['reference_type_id'].initial = ref_type.id

    context = {'comment_list': queryset,
               'form': form}

    return context