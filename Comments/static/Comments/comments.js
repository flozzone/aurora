/**
 * Created by dan on 12/21/13.
 */
$(document).ready( function() {
//    updateComments(true);
    registerTestButton();
    registerReplyLinks();
    registerReplyButton();
});

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
//    $('#commentTextarea').focus

function registerReplyButton() {
    $('#post_reply').click( function(event) {
        event.preventDefault();
        $.ajax({
            url: '/post_reply/',
            data: $(this).closest('form').serialize(),
            type: 'POST',
            dataType: 'html',
            success: function(response) {
                $("#replyTextarea").val('');
                $('#replyForm').hide();
                updateComments(false);
            }
        })
        return false;
    })
}

function postComment() {
    $.ajax({
        url: "/post_comment/",
        data: $("#commentForm").serialize(),
        type: "POST",
        // the type of data we expect back
        dataType: 'html',
        success: function (response) {
            $("#commentText").val('');
            updateComments(false);
        },
        error: function (xhr, status) {
        },
        complete: function (xhr, status) {
        }
    });
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
                registerReplyButton();
            }
        },
        complete: function(xhr, status) {
            if(keepPolling == true) {
                setTimeout('updateComments(true);', 5000);
            }
        }
    })
}

function postReply(id) {
    alert("post reply");
}

function registerTestButton() {
    $('#myTest').click(function () {
//    updateComments(false);
//    alert(x.toString() + " # " + y.toString());
//    var currentId = $('.comment').first().attr('id');
//    console.log(currentId);
//    placeForm();
        updateComments(false);
//        $('#commentForm').toggle();
//        console.log($('#id_parent_comment').val());
//        $('#replyForm').toggle();
//        $('#replyForm').hide();
//        console.log($('#id_parent_comment').val());
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
