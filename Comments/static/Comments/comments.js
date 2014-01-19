/**
 * Created by dan on 12/21/13.
 */

var stop_update_poll = false;
var polling_interval = 5000;
var current_poll_timeout;

$(document).ready( function() {
    registerTestButton();
    registerStartPolling();
    registerStopPolling();

    registerReplyLinks();
    registerDeleteLinks();
    registerTextareas();
    registerReplyButton();
    registerCancelReplyButton();

    registerAddCommentFormButtons();
    registerAddCommentButton();
    registerCancelCommentButton();
    registerVotes();

    updateComments(true, false);
});

function registerStopPolling() {
    $('#stopPolling').click(function (event) {
        event.preventDefault();
        stopPolling();
        return false;
    })
}

function registerStartPolling() {
    $('#startPolling').click(function (event) {
        event.preventDefault();
        startPolling();
        return false;
    })
}

function registerVotes() {
    $('.comment_list').each( function() {
        registerVoteForCommentList($(this));
    });
}

function registerVoteForCommentList($comment_list) {
    $comment_list.find('.vote_down_on, .vote_up_on').click( function(event) {
        event.preventDefault();
        var direction;
        if($(this).attr('class') == 'vote_up_on') direction = 'up'
        else direction = 'down';
        $.ajax({
            url: '/vote_on_comment/',
            data: {
                direction: direction,
                comment_id: $(this).attr('data-comment_number')
            },
            type: 'GET',
            dataType: 'html',
            success: function(response) {
                updateComments(false, true);
            }
        })
        return false;
    })
}

function registerAddCommentFormButtons() {
    $('.button_add_comment_form').each( function() {
        registerAddCommentFormButton($(this));
    })
}

function registerAddCommentFormButton($button) {
    $button.click( function(event) {
        event.preventDefault();

        var ref_id = $(this).attr('data-ref_id');
        var ref_type = $(this).attr('data-ref_type');
        var $commentForm = $('#commentForm');
        var $form_ref_id = $commentForm.find('#id_reference_id')
        var $form_ref_type = $commentForm.find('#id_reference_type_id')
        $form_ref_id.val(ref_id);
        $form_ref_type.val(ref_type);
        if($commentForm.is(':visible')) {
            $commentForm.prev().show();
        }
        $commentForm.show()
        $(this).after($commentForm);
        $(this).hide();

        return false;
    })
}

function registerReplyLinks() {
    $('.comment_list').each( function () {
        registerReplyLinksForCommentList($(this));
    });
}

function registerReplyLinksForCommentList($comment_list) {

    $comment_list.find('[id^=comment_reply_link_]').click( function(event) {
        event.preventDefault();
        var $replyForm = $('#replyForm');

        var commentId = $(this).attr('data-reply_to');
        $replyForm.find('#id_parent_comment').attr('value', commentId);

        var ref_obj = findClosestRefObj(this);
        $replyForm.find('#id_reference_id').attr('value', ref_obj.id);
        $replyForm.find('#id_reference_type_id').attr('value', ref_obj.type);

        var $textArea = $('#replyTextarea');
        var user = $(this).closest('.comment, .response').attr('data-comment_author');
        var new_text = $textArea.val();
        new_text = new_text.replace(/(@[^ ]+\s|^)/, '@' + user + ' ');
        $textArea.val(new_text);

        $(this).after($replyForm);
        $replyForm.show();
        return false;
    });
}

function registerDeleteLinks() {
    $('.comment_list').each( function () {
        registerDeleteLinksForCommentList($(this));
    });
}

function registerDeleteLinksForCommentList($comment_list) {
    $comment_list.find('.delete_comment, .delete_response').click( function(event) {
        event.preventDefault();
        deleteComment($(this).attr('data-delete_id'));
        updateCommentList(false, true, $comment_list);
        return false;
    });
}

function deleteComment(comment_id) {
    console.log('delete comment ' + comment_id.toString());
    $.ajax({
        url: '/delete_comment/',
        data: { comment_id: comment_id },
        type: 'POST',
        dataType: 'json',
        beforeSend: function(xhr, settings) {
            var csrftoken = getCsrfToken();
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    })
}

function getCsrfToken() {
    return $('[name=csrfmiddlewaretoken]').first().val();
}

function registerTextarea($text_area) {
    $text_area.focusin( function() {
        stopPolling();
    })

    $text_area.focusout( function() {
        startPolling();
    })
}

function registerReplyTextarea() {
    registerReplyTextarea($('#replyTextarea'));
}

function registerTextareas() {
    $('#replyTextarea, #commentTextarea').each( function() {
        registerTextarea($(this));
    });
}

function registerReplyButton() {
    $('#button_post_reply').click( function(event) {
        event.preventDefault();
        $.ajax({
            url: '/post_reply/',
            data: $(this).closest('form').serialize(),
            type: 'POST',
            dataType: 'html',
            success: function(response) {
                $('#replyForm').hide();
                $("#replyTextarea").val('');
                updateComments(false, true);
            }
        })
        return false;
    })
}

function registerCancelReplyButton() {
    $('#button_cancel_reply').click( function(event) {
        event.preventDefault();
        $('#replyForm').hide();
        $('#replyTextarea').val('');
        return false;
    })
}

function hideCommentForm() {
    var $form =  $('#commentForm');
    $form.hide();
    $('#commentTextarea').val('');
    $form.prev().show();
}

function registerCancelCommentButton() {
    $('#button_cancel_comment').click( function(event) {
        event.preventDefault();
        hideCommentForm();
        return false;
    })
}

function registerAddCommentButton() {
    $('#button_add_comment').click(function (event) {
        event.preventDefault();

        $.ajax({
            url: "/post_comment/",
            data: $("#commentForm").serialize(),
            type: "POST",
            // the type of data we expect back
            dataType: 'html',
            success: function (response) {
                hideCommentForm();
                updateComments(false, true);
            },
            error: function (xhr, status) {
            },
            complete: function (xhr, status) {
            }
        });

        return false;
    })
}

/**
 * updates a comment_list by sending highest comment id to server and replacinng the div with the answer if one is
 * being received
 * @param keepPolling   should updateComments keep polling for updates after call
 * @param force         force a reload of the comment_list
 */
function updateComments(keepPolling, force) {
    updateCommentList(keepPolling, force, $('.comment_list').first());
    $('.comment_list').not(':first').each( function() {
        updateCommentList(false, force, $(this));
    })
}

function updateCommentList(keepPolling, force, $comment_list) {;
    var maxComment;     // comment with highest ID in current $comment_list
    if (force) {
        maxComment = {
            ref_type: $comment_list.attr('data-ref_type'),
            ref_id: $comment_list.attr('data-ref_id'),
            id: -1
        }
    } else {
        maxComment = getCommentWithMaxId($comment_list);
    }

    $.ajax({
        url: '/update_comments/',
        data: maxComment,
        type: 'GET',
        dataType: 'html',
        success: function (html) {
            if (html != '') {
                var ref_type = $comment_list.attr('data-ref_type');
                var ref_id = $comment_list.attr('data-ref_id');

                // reply form replacement & conservation
                var $reply_form_parent_info = $comment_list.find('#id_parent_comment');
                if ($reply_form_parent_info.length > 0) {
                    // save current replyForm so it isn't deleted by the div update
                    var $replyForm = $('#replyForm');
                    var current_parent_comment_id = $comment_list.find('#id_parent_comment').val();
                    $comment_list.replaceWith(html);
                    $('#comment_reply_link_' + current_parent_comment_id).parent().append($replyForm);
                    registerReplyButton();
                    registerReplyTextarea();
                } else {
                    $comment_list.replaceWith(html);
                }

                // get us the new comment list for the ref_object
                $comment_list = $('.comment_list').filter('[data-ref_type=' + ref_type + ']')
                    .filter('[data-ref_id=' + ref_id + ']');
                // only reregister replaced elements to avoid multi registration
                registerReplyLinksForCommentList($comment_list);
                registerVoteForCommentList($comment_list);
                registerDeleteLinks();
            }
        },
        complete: function (xhr, status) {
            if (keepPolling == true && !stop_update_poll) {
                current_poll_timeout = setTimeout('updateComments(true, false)', polling_interval);
            }
        }
    })
}

function stopPolling() {
    clearTimeout(current_poll_timeout);
    stop_update_poll = true;
}

function startPolling() {
    stop_update_poll = false;
    updateComments(true, false);
}

function registerTestButton() {
    $('#myTest').click(function () {
//    updateComments(false);
//    alert(x.toString() + " # " + y.toString());
//    var currentId = $('.comment').first().attr('id');
//    console.log(currentId);
//    placeForm();
        updateComments(false, true);
//        $('#commentForm').toggle();
//        console.log($('#id_parent_comment').val());
//        $('#replyForm').toggle();
//        $('#replyForm').hide();
//        console.log($('#id_parent_comment').val());
//        if(stop_update_poll) startPolling();
//        else stopPolling();
        return false;
    })
}

function findClosestRefObj(child) {
    var ref_type = $(child).closest('[data-ref_type]').attr('data-ref_type');
    var ref_id = $(child).closest('[data-ref_id]').attr('data-ref_id');
    return { type: ref_type, id: ref_id }
}

function getCommentWithMaxId($comment_list) {
    var maxComment = {id: -1,
                      ref_type: $comment_list.attr('data-ref_type'),
                      ref_id: $comment_list.attr('data-ref_id')}
    var id;
    $comment_list.find('.comment, .response').each(function() {
        id = parseInt( $(this).attr('data-comment_number') );
        if (id > maxComment.id) {
            maxComment.id = id;

            var ref_obj = findClosestRefObj(this);
            maxComment.ref_id = ref_obj.id;
            maxComment.ref_type = ref_obj.type;
        }
    })
    return(maxComment);
}
