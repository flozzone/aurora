from django import template
from django.contrib.contenttypes.models import ContentType
from Comments.models import Comment, CommentList
from Comments.views import CommentForm, ReplyForm
from django.template.loader import render_to_string
from PortfolioUser.models import PortfolioUser

register = template.Library()

# {% get_comment_list for [object] as [varname] %}
# {% render_comment_list for [object] %}


class CommentListNode(template.Node):
    def __init__(self, reference):
        self.reference_var = template.Variable(reference)
        self.template = 'Comments/comments_with_forms.html'

    def render(self, context):
        try:
            ref_object = self.reference_var.resolve(context)
            ref_type = ContentType.objects.get_for_model(ref_object)

            # user = PortfolioUser.objects.get(id=context['user'].id)
            user = context['user']

            queryset = Comment.query_top_level_sorted(ref_object.id, ref_type.id, user)
            revision = CommentList.get_or_create(ref_object).revision

            form = CommentForm()
            form.fields['reference_id'].initial = ref_object.id
            form.fields['reference_type_id'].initial = ref_type.id
            form.fields['visibility'].initial = Comment.PUBLIC
            reply_form = ReplyForm()
            reply_form.fields['reference_id'].initial = ref_object.id
            reply_form.fields['reference_type_id'].initial = ref_type.id
            reply_form.fields['parent_comment'].initial = -1
            reply_form.fields['visibility'].initial = Comment.PUBLIC

            id_suffix = "_" + str(ref_object.id) + "_" + str(ref_type.id)
            context.update({'comment_list': queryset,
                            'form': form,
                            'reply_form': reply_form,
                            'ref_type': ref_type.id,
                            'ref_id': ref_object.id,
                            'id_suffix': id_suffix,
                            'requester': user,
                            'revision': revision})

            return render_to_string(self.template, context)
        except template.VariableDoesNotExist:
            return ''


class AdditionalCommentListNode(CommentListNode):
    def __init__(self, reference):
        self.reference_var = template.Variable(reference)
        self.template = 'Comments/additional_comments.html'


class MultiCommentListNode(CommentListNode):
    def __init__(self, reference):
        self.reference_var = template.Variable(reference)
        self.template = 'Comments/multi_comment.html'


@register.tag
# def render_comment_list_plain_tag(parser, token):
def render_comment_list(parser, token):
    """
    Renders a complete comment list with scripts and forms. Use this at max once per document.
    """
    ref_token = handle_tokens(token)
    return CommentListNode(ref_token)


@register.tag
def render_additional_comment_list(parser, token):
    """
    Comment List without any scripting or forms.
    You need to load something like comments_boilerplate + comments js files or render_comment_list to make
    this tags comment list work.
    """
    ref_token = handle_tokens(token)
    return AdditionalCommentListNode(ref_token)


@register.tag
def render_multi_comment_list(parser, token):
    """
    Comment List with JS but without forms. Use this for comment lists that are loaded dynamically and not during
    document load time. Use this in conjunction with comments_boilerplate to make the this tags comment_list work.
    """
    ref_token = handle_tokens(token)
    return MultiCommentListNode(ref_token)


@register.simple_tag(takes_context=True)
def comments_count(context, for_string, ref_obj):
    ref_id, ref_type = ref_object_to_id_type(ref_obj)
    requester = context['user']
    return Comment.query_number_of_all(ref_id, ref_type, requester)


def handle_tokens(token):
    tokens = token.split_contents()
    usage = 'template tag has to look like this: {% ' \
            + tokens[0] + ' for <reference> %}'

    if len(tokens) != 3:
        raise template.TemplateSyntaxError(usage)

    if tokens[1] != 'for':
        raise template.TemplateSyntaxError(usage)

    return tokens[2]


def token_to_ref_id_type(token, context):
    reference_var = template.Variable(token)
    ref_object = reference_var.resolve(context)
    ref_type = ContentType.objects.get_for_model(ref_object)
    ref_id = ref_type.id
    return ref_id, ref_type


def ref_object_to_id_type(ref_object):
    object_type = ContentType.objects.get_for_model(ref_object)
    object_pk = ref_object.id
    return object_pk, object_type.id


@register.inclusion_tag('Comments/comments_with_forms.html')
def render_comment_list_inclusion_tag(for_string, reference):
    from Comments.views import CommentForm
    from Comments.models import Comment

    ref_type = ContentType.objects.get_for_model(reference)

    queryset = Comment.objects.filter(
        parent=None,
        content_type__pk=ref_type.id,
        object_id=reference.id).order_by('-post_date')

    form = CommentForm()
    form.fields['reference_id'].initial = reference.id
    form.fields['reference_type_id'].initial = ref_type.id

    context = {'comment_list': queryset,
               'form': form,
               'ref_type': ref_type.id,
               'ref_id': reference.id}

    return context

@register.inclusion_tag('Comments/forms.html', takes_context=True)
def comments_boilerplate(context):
    """
    Renders only the forms for one or more comment lists. No scripts are being loaded.
    """

    form = CommentForm()
    form.fields['visibility'].initial = Comment.PUBLIC
    reply_form = ReplyForm()
    reply_form.fields['parent_comment'].initial = -1
    reply_form.fields['visibility'].initial = Comment.PUBLIC

    user = context['user']

    context.update({'form': form,
                    'reply_form': reply_form,
                    # 'ref_type': ref_type.id,
                    # 'ref_id': ref_object.id,
                    # 'id_suffix': id_suffix,
                    'requester': user})
                    # 'revision': revision}

    return context
