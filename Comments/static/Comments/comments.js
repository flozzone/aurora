/**
 * Created by dan on 12/21/13.
 */

//"use strict";

var POLLING = {
    stopped: false,
    current_interval: 5000,
    active_interval: 5000,
    idle_interval: 60000,
    increase_interval: function() {
        POLLING.current_interval = Math.min(POLLING.current_interval * 2, POLLING.idle_interval);
    },
    firstRefId: null,
    lastRefId: null
};

var state = {
    modifying: false,
    posting: false
};

$(document).ready( function() {
    registerTestButton();
    registerStartPolling();
    registerStopPolling();

    $('.comment_list').each( function () {
        $(this).find('*').off();
        registerElementsForCommentList($(this))
    });

    registerReplyButton();
    registerCancelReplyButton();

    registerAddCommentFormButtons();
    registerAddCommentButton();
    registerCancelCommentButton();

    registerPolling();

    startPolling();
});

function registerElementsForCommentList($comment_list) {
    registerReplyLinksForCommentList($comment_list);
    registerEditLinksForCommentList($comment_list);
    registerDeleteLinksForCommentList($comment_list);
    registerVoteForCommentList($comment_list);
    registerPromoteLinksForCommentList($comment_list);
//    registerBookmarkLinksForCommentList($comment_list);
    Bookmarks.registerForCommentList($comment_list);
}

function registerPolling() {
    $(window).off('blur');
    $(window).blur( function() {
        POLLING.current_interval = POLLING.idle_interval;
    })
    $(window).off('focus');
    $(window).focus( function() {
        POLLING.current_interval = POLLING.active_interval;

        if(!state.modifying && !state.posting) {
            startPolling();
        }
    })
}

function registerStopPolling() {
    $('#stopPolling').off();
    $('#stopPolling').click( function(event) {
        event.preventDefault();
        stopPolling();
        return false;
    })
}

function registerStartPolling() {
    $('#startPolling').off();
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
                updateCommentLists(false);
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
    $button.off();
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

        /**
         *
         * @param n the node to convert to string with '\n'
         * @returns {string}
         */
        function getText(n) {
            var rv = '';

            if (n.nodeType == 3) {
                rv = n.nodeValue;
            } else {
                for (var i = 0; i < n.childNodes.length; i++) {
                    rv += getText(n.childNodes[i]);
                }
                var d = getComputedStyle(n).getPropertyValue('display');
                if (d.match(/^block/) || d.match(/list/) || n.tagName == 'BR') {
                    rv += "\n";
                }
            }

            return rv;
        };

        var $save = $('#edit_save');
        $save.off();
        $save.click( function(event) {
            event.preventDefault();

//            var text = $commentText.html().trim()
//            text = text.replace(/<div>[\s\r\n]*<br>[\s\r\n]*<\/div>/g, "<br>");
//            text = text.replace(/(<\/p>)|(<\/div>)/g, "");
//            text = text.replace(/(<br><\/br>)|(<br>)|(<br \/>)|(<p>)|(<div>)/g, "\r\n");
//            text = text.replace(/(<br><\/br>)|(<br>)|(<br \/>)|(<p>)|(<\/p>)|(<div>)|(<\/div>)/g, "\r\n");

            var text = getText($commentText.get(0)).trim();

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

        function deleteComment() {
            $.ajax({
                url: '/delete_comment/',
                data: { comment_id: comment_number },
                type: 'POST',
                dataType: 'json',
                beforeSend: function (xhr, settings) {
                    var csrftoken = getCsrfToken();
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                },
                complete: function (xhr, status) {
                    endDelete();
                }
            })
        }

        function endDelete() {
            $delete_buttons.hide();
            $('#element_shelter').append($delete_buttons);
            startPolling();
            state.modifying = false;
        }

        var $delete_cancel = $('#delete_cancel');
        $delete_cancel.off();
        $delete_cancel.click( function(event) {
            event.preventDefault();
            endDelete();
            $actions.show();
            return false;
        });

        var $delete_confirm = $('#delete_confirm');
        $delete_confirm.off();
        $delete_confirm.click( function(event) {
            event.preventDefault();
            deleteComment();
            return false;
        })

        return false;
    });
}

function getCsrfToken() {
    return $('[name=csrfmiddlewaretoken]').first().val();
}

function registerReplyButton() {
    $('#button_post_reply').off();
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
                startPolling();
                state.posting = false;
            }
        })
        return false;
    })
}

function registerCancelReplyButton() {
    $('#button_cancel_reply').off();
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
    $('#button_cancel_comment').off();
    $('#button_cancel_comment').click( function(event) {
        event.preventDefault();
        hideCommentForm();
        state.posting = false;
        startPolling();
        return false;
    })
}

function registerAddCommentButton() {
    $('#button_add_comment').off();
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

//(function() {
/**
 * updates a comment_list by sending highest comment id to server and replacinng the div with the answer if one is
 * being received
 * @param keepPolling   should updateCommentLists keep polling for updates after call
 * @param force         force a reload of the comment_list
 */
function updateComments(keepPolling) {
    var $comment_lists = $('.comment_list')
    updateCommentList(keepPolling, $comment_lists.first());
    $comment_lists.not(':first').each( function() {
        updateCommentList(false, $(this));
    });
}

function updateCommentLists(keepPolling) {
    var data = {revisions: getRevisions()};

    $.ajax({
        url: '/update_comments/',
        data: data,
        type: 'GET',
        dataType: 'json',
        success: function (json) {
            var comment_list_updates = json['comment_list_updates'];
            if(comment_list_updates.length > 0) {
                handleCommentListUpdates(comment_list_updates);
            }
            if (json['polling_active_interval']) {
                POLLING.active_interval = json['polling_active_interval'];
            }
            if (json['polling_idle_interval']) {
                POLLING.idle_interval = json['polling_idle_interval'];
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            POLLING.increase_interval();
        },
        complete: function (xhr, status) {
            if (keepPolling == true && !POLLING.stopped) {
                clearTimeout(POLLING.current_timeout);
                POLLING.current_timeout = setTimeout('updateCommentLists(true)', POLLING.current_interval);
            }
        }
    })
}

function findCommentListByRef(ref_id, ref_type) {
    return $('.comment_list').filter('[data-ref_type=' + ref_type + ']')
        .filter('[data-ref_id=' + ref_id + ']');
}

function handleCommentListUpdates(comment_list_updates) {
    var ref_id, ref_type, html;
    var $comment_list;

    for(var i = 0; i < comment_list_updates.length; i++) {
        ref_id = comment_list_updates[i].ref_id;
        ref_type = comment_list_updates[i].ref_type;
        html = comment_list_updates[i].comment_list;

        $comment_list = findCommentListByRef(ref_id, ref_type);
        replaceCommentListWithHtml($comment_list, html)
    }
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
    clearTimeout(POLLING.current_timeout);
    POLLING.stopped = true;
}

function startPolling() {
    POLLING.stopped = false;
    updateCommentLists(true);
}

function setActivePollingObjects(firstRefId, lastRefId) {
    POLLING.firstRefId = firstRefId;
    POLLING.lastRefId = lastRefId;

    console.log('firstRefId: ' + firstRefId.toString());
    console.log('lastRefId: ' + lastRefId.toString());

    updateCommentLists(false);
}

//});

function getRevisions() {
    var revisions = [];
    var ref_id;

    var $comment_lists = $('.comment_list')
    $comment_lists.each(function () {
        var $this = $(this);
        ref_id = $this.attr('data-ref_id');
        if(POLLING.firstRefId !== null) {
            if(ref_id < POLLING.firstRefId || ref_id > POLLING.lastRefId) {
                return true;
            }
        }

        revisions.push({
            number: $this.attr('data-revision'),
            ref_type: $this.attr('data-ref_type'),
            ref_id: ref_id
        });
    });

    return revisions;
}

function getRevision($comment_list) {
    return {id: $comment_list.attr('data-revision'),
        ref_type: $comment_list.attr('data-ref_type'),
        ref_id: $comment_list.attr('data-ref_id')}
}

function registerTestButton() {
    $('#myTest').off();
    $('#myTest').on('click', function(){
//        editElements.prop = 'bam';
//        editElements();
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
        alert('nothing assigned');
//        $('*').off();
        return false;
    });
}

function findClosestRefObj($child) {
    var ref_type = $child.closest('[data-ref_type]').attr('data-ref_type');
    var ref_id = $child.closest('[data-ref_id]').attr('data-ref_id');
    return { type: ref_type, id: ref_id }
}
