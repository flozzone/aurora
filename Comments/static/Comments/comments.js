/**
 * Created by dan on 12/21/13.
 */

var stop_update_poll = false;
var current_poll_timeout;

$(document).ready( function() {
    registerTestButton();
    registerStartPolling();
    registerStopPolling();

    registerReplyLinks();
    registerReplyButton();
    registerReplyTextarea();
    registerCancelReplyButton();
    registerAddCommentButton();


    updateComments(true);
});

function registerStopPolling() {
    $('#stopPolling').click(function (event) {
        event.preventDefault();
        console.log('stopPolling');
        stopPolling();
        return false;
    })
}

function registerStartPolling() {
    $('#startPolling').click(function (event) {
        event.preventDefault();
        console.log('startPolling');
        startPolling();
        return false;
    })
}

function registerReplyLinks() {
    $('[id^=comment_reply_link_]').click(function(event) {
        event.preventDefault();
        var replyForm = $('#replyForm');
        var commentId = $(this).attr('data-reply_to');
        replyForm.find('#id_parent_comment').attr('value', commentId);
        $(this).parent().append(replyForm);
        replyForm.show();
        return false;
    })
}

function registerReplyTextarea() {
    var $replyTextarea = $('#replyTextarea');

    $replyTextarea.focusin( function() {
        stopPolling();
    })

    $replyTextarea.focusout( function() {
        startPolling();
    })
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
                updateComments(false);
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
                $("#commentTextarea").val('');
                updateComments(false);
            },
            error: function (xhr, status) {
            },
            complete: function (xhr, status) {
            }
        });
        return true;
    })
}

function formSubmitButton() {
    $("#commentForm").submit(function (event) {
        event.preventDefault();

        $.ajax({
            url: "/post_comment/",
            data: $(this).serialize(),
            type: "POST",
            // the type of data we expect back
            dataType: "json",
            success: function (json) {
                alert($("#commentText").val)
                $("<h1/>").text("Yay").appendTo("body");
                alert(json['text']);
            },
            error: function (xhr, status) {
                alert("Sorry, there was a problem!");
            },
            complete: function (xhr, status) {
                alert("Request completed successfully");
            }
        });
        return false;
    });
}

function updateComments(keepPolling) {
    $.ajax({
        url: '/update_comments/',
        data: getCommentWithMaxId(),
        type: 'GET',
        dataType: 'html',
        success: function (html) {
            if(html != '') {
                var current_parent_comment_id = $('#id_parent_comment').val();
                var $comments = $('#comments');
                var $replyForm = $('#replyForm');
                $comments.replaceWith(html);
                $('#comment_reply_link_' + current_parent_comment_id).parent().append($replyForm);
                registerReplyLinks();
//                registerReplyButton();
            }
        },
        complete: function(xhr, status) {
            if(keepPolling == true && !stop_update_poll) {
                current_poll_timeout = setTimeout('updateComments(true);', 5000);
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
    updateComments(true);
}

function registerTestButton() {
    $('#myTest').click(function () {
//    updateComments(false);
//    alert(x.toString() + " # " + y.toString());
//    var currentId = $('.comment').first().attr('id');
//    console.log(currentId);
//    placeForm();
//        updateComments(false);
//        $('#commentForm').toggle();
//        console.log($('#id_parent_comment').val());
//        $('#replyForm').toggle();
//        $('#replyForm').hide();
//        console.log($('#id_parent_comment').val());
        if(stop_update_poll) startPolling();
        else stopPolling();
        return false;
    })
}

function getCommentWithMaxId() {
    var maxComment = {id: -1,
                      ref_type: -1,
                      ref_id: -1}
    var id;
    $('.comment, .response').each(function() {
        id = parseInt( $(this).attr('data-comment_number') );
        if (id > maxComment.id) {
            maxComment.id = id;
            maxComment.ref_type= $(this).closest('[data-ref_type]').attr('data-ref_type');
            maxComment.ref_id = $(this).closest('[data-ref_id]').attr('data-ref_id');
        }
    })
    return(maxComment);
}
