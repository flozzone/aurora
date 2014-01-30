/**
 * Created by dan on 12/21/13.
 */

var stop_update_poll = false;
var polling_interval = 5000;
var current_poll_timeout;

var state = {
    modifying: false,
    posting: false
}

$(document).ready( function() {
    registerTestButton();
    registerStartPolling();
    registerStopPolling();

    $('.comment_list').each( function () {
        registerElementsForCommentList($(this))
    });

    registerReplyButton();
    registerCancelReplyButton();

    registerAddCommentFormButtons();
    registerAddCommentButton();
    registerCancelCommentButton();

    updateComments(true, false);
});

function registerElementsForCommentList($comment_list) {
    registerReplyLinksForCommentList($comment_list);
    registerEditLinksForCommentList($comment_list);
    registerDeleteLinksForCommentList($comment_list);
    registerVoteForCommentList($comment_list);
    registerPromoteLinksForCommentList($comment_list);
    registerBookmarkLinksForCommentList($comment_list)
}

function registerStopPolling() {
    $('#stopPolling').click( function(event) {
        event.preventDefault();
        stopPolling();
        return false;
    })
}

function registerStartPolling() {
    $('#startPolling').click( function(event) {
        event.preventDefault();
        startPolling();
        return false;
    })
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

        if(state.modifying)
            return false;
        state.posting = true;

        stopPolling();
        $('#replyForm').hide();

        var ref_id = $(this).attr('data-ref_id');
        var ref_type = $(this).attr('data-ref_type');
        var $commentForm = $('#commentForm');
        $commentForm.find('#id_reference_id').val(ref_id);
        $commentForm.find('#id_reference_type_id').val(ref_type);
        if($commentForm.is(':visible')) {
            $commentForm.prev().show();
        }
        $(this).after($commentForm);
        var reply_text = $('#replyForm').find('textarea').val();
        if(reply_text != '') {
            reply_text = reply_text.replace(/(@[^ ]+\s|^)/, '');
           $commentForm.find('textarea').val(reply_text);
        }
        $commentForm.show()
        $(this).hide();

        return false;
    })
}

function registerEditLinksForCommentList($comment_list) {
    $comment_list.find('.edit_link').click( function(event) {
        event.preventDefault();

        if(state.posting || state.modifying)
            return false;
        state.modifying = true;

//        var $replyForm = $('#replyForm');
//        var $commentForm = $('#commentForm');
        var $editButtons = $('#edit_buttons');

        stopPolling();

        var $comment = $(this).closest('.comment, .response');
        var $commentText = $comment.find('.comment_text, .response_text');
        var $actions = $(this).closest('.comment_actions, .response_actions');
        var oldCommentText = $commentText.html();

        $commentText.attr('contenteditable', true);
        $actions.after($editButtons);
        $actions.hide();
        $editButtons.show();

        function endEdit() {
            $actions.show();
            $('#element_shelter').append($editButtons);
            $editButtons.hide();
            $commentText.attr('contenteditable', false);

            state.modifying = false;
            startPolling();
        }

        var $cancel = $('#edit_cancel');
        $cancel.off();
        $cancel.click( function(event) {
            event.preventDefault();

            $commentText.html(oldCommentText);

            endEdit();

            return false;
        });

        var $save = $('#edit_save');
        $save.off();
        $save.click( function(event) {
            event.preventDefault();

            var text = $commentText.html().trim()
            text = text.replace(/(<br><\/br>)|(<br>)|(<br \/>)|(<p>)|(<\/p>)|(<div>)|(<\/div>)/g, "\r\n");

            var data = {comment_id: $comment.attr('data-comment_number'),
                        text: text}

            $.ajax({
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
                },
                url: '/edit_comment/',
                crossDomain: false,
                data: data,
                type: 'POST',
                dataType: 'html',
                success: function (response) {
                    endEdit();
                },
                complete: function(xhr, status) {
//                    $formTextarea.val('');
                }
            });

            return false;
        });

        return false;
    });
}

function registerReplyLinksForCommentList($comment_list) {
    $comment_list.find('[id^=reply_comment_link_]').click( function(event) {
        event.preventDefault();

        if(state.modifying)
            return false;
        state.posting = true;

        stopPolling();

        var $replyForm = $('#replyForm');

        var comment_number = $(this).attr('data-reply_to');
        setCommentId($replyForm, comment_number);

        var user = $(this).closest('.comment, .response').attr('data-comment_author');

        var $commentTextarea = $('#commentTextarea');
        var $replyTextarea = $('#replyTextarea');
        if($commentTextarea.val() != '') {
            var new_text = $commentTextarea.val();
        } else {
            var new_text = $replyTextarea.val();
        }
        new_text = new_text.replace(/(@[^ ]+\s|^)/, '@' + user + ' ');
        $replyTextarea.val(new_text);

        $(this).after($replyForm);
        hideCommentForm();
        $replyForm.show();
        return false;
    });
}

function setCommentId($form, comment_number) {
    $form.find('#id_parent_comment').attr('value', comment_number);

    var $comment = $('[data-comment_number=' + comment_number + ']');
    var ref_obj = findClosestRefObj($comment);
    $form.find('#id_reference_id').attr('value', ref_obj.id);
    $form.find('#id_reference_type_id').attr('value', ref_obj.type);
}

function registerDeleteLinksForCommentList($comment_list) {
    $comment_list.find('.delete_comment, .delete_response').click( function(event) {
        event.preventDefault();

        if(state.modifying || state.posting)
            return false;

        stopPolling();
        state.modifying = true;

        var $delete_buttons = $('#delete_buttons');
        var $actions = $(this).closest('.comment_actions, .response_actions');
        $actions.after($delete_buttons);
        $actions.hide();
        $delete_buttons.show();

        var comment_number = $(this).attr('data-delete_id');

        function endDelete() {
            $delete_buttons.hide();
            $('#element_shelter').append($delete_buttons);
            $actions.show();
            state.modifying = false;
            updateCommentList(false, true, $comment_list);
            startPolling();
        }

        var $delete_cancel = $('#delete_cancel');
        $delete_cancel.off();
        $delete_cancel.click( function(event) {
            event.preventDefault();
            endDelete();
            return false;
        });

        var $delete_confirm = $('#delete_confirm');
        $delete_confirm.off();
        $delete_confirm.click( function(event) {
            event.preventDefault();
            deleteComment(comment_number);
            endDelete();
            return false;
        })

        return false;
    });
}

function deleteComment(comment_id) {
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
        state.posting = false;
        return false;
    })
}

function registerCancelReplyButton() {
    $('#button_cancel_reply').click( function(event) {
        event.preventDefault();
        $('#replyForm').hide();
        $('#replyTextarea').val('');
        state.posting = false;
        startPolling();
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
        state.posting = false;
        startPolling();
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
                startPolling();
            },
            error: function (xhr, status) {
            },
            complete: function (xhr, status) {
            }
        });

        state.posting = false;
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
    var $comment_lists = $('.comment_list')
    updateCommentList(keepPolling, force, $comment_lists.first());
    $comment_lists.not(':first').each( function() {
        updateCommentList(false, force, $(this));
    });
}

function updateCommentList(keepPolling, force, $comment_list) {
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
        dataType: 'json',
        success: function (json) {
            var html = json['comment_list'];
            if (html) {
                replaceCommentListWithHtml($comment_list, html)
            }
            if (json['polling_interval']) {
                polling_interval = json['polling_interval']
            }
        },
        complete: function (xhr, status) {
            if (keepPolling == true && !stop_update_poll) {
                current_poll_timeout = setTimeout('updateComments(true, false)', polling_interval);
            }
        }
    })
}

function findCommentListByRef(ref_id, ref_type) {
    return $('.comment_list').filter('[data-ref_type=' + ref_type + ']')
        .filter('[data-ref_id=' + ref_id + ']');
}

function replaceCommentListWithHtml($comment_list, html) {
    var ref_type = $comment_list.attr('data-ref_type');
    var ref_id = $comment_list.attr('data-ref_id');

    // reply form replacement & conservation
    var $replyForm = $comment_list.find('#replyForm');
    if ($replyForm.length > 0) {
        // save current replyForm so it isn't deleted by the div update
        var prev_id = $replyForm.prev().attr('id')
        var parent_comment_number = $comment_list.find('#id_parent_comment').val();
        var parent_comment_id = $('[data-comment_number=' + parent_comment_number + ']');
        $comment_list.replaceWith(html);

        var $new_prev = $('#' + prev_id);
        if($new_prev.length > 0) {
            $new_prev.after($replyForm);
        } else {
            var $parent_comment = $('[data-comment_number=' + parent_comment_number + ']');
            if($parent_comment > 0) {
                $parent_comment.append($replyForm);
            } else {
                $comment_list = findCommentListByRef(ref_id, ref_type);
                $comment_list.prepend($replyForm);
                $replyForm.hide();
            }
        }

        registerReplyButton();
        registerCancelReplyButton();
    } else {
        $comment_list.replaceWith(html);
    }

    // get us the new comment list for the ref_object
    $comment_list = findCommentListByRef(ref_id, ref_type);

    // only reregister replaced elements to avoid multi registration
    registerElementsForCommentList($comment_list);
}

function stopPolling() {
    clearTimeout(current_poll_timeout);
    stop_update_poll = true;
}

function startPolling() {
    if(stop_update_poll == false)
        return

    stop_update_poll = false;
    updateComments(true, false);
}

function registerTestButton() {
    $('#myTest').on('click', function(){
        editElements.prop = 'bam';
        editElements();
//    $('#myTest').click(function () {
//    updateComments(false);
//    alert(x.toString() + " # " + y.toString());
//    var currentId = $('.comment').first().attr('id');
//    console.log(currentId);
//        updateComments(false, true);
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

function findClosestRefObj($child) {
    var ref_type = $child.closest('[data-ref_type]').attr('data-ref_type');
    var ref_id = $child.closest('[data-ref_id]').attr('data-ref_id');
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

            var ref_obj = findClosestRefObj($(this));
            maxComment.ref_id = ref_obj.id;
            maxComment.ref_type = ref_obj.type;
        }
    })
    return(maxComment);
}
