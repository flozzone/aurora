/**
 * Created by dan on 12/21/13.
 */
$(document).ready( function() {
    updateComments(true);
    registerReplyLinks();
    registerTestButton();
});

function registerReplyLinks() {
    $('[id^=reply_to_]').click(function() {
        var replyForm = $('#replyForm');
        $(this).parent().append(replyForm);
        replyForm.show();
        return false;
    })
}
//    $('#commentTextarea').focus

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
//            $('#comments').prepend(response)
        },
        error: function (xhr, status) {
//            alert("Sorry, there was a problem!");
        },
        complete: function (xhr, status) {
        }
    });
//    console.log(response); // undefined
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

function placeForm() {
//    $('#commentForm').append()
//    look for form
//    if form doesnt exist: create
//    if it does exist: unhide
//    that.append($('<h1/>').text('blub'));
//    alert(that.text);
//    console.log(that);
//    that.parent().appendChild('<p>hihi</>');
//    $('.comment#' + currentId.toString()).parent().append('<p>blub</b>');
}

function updateComments(keepPolling) {
    $.ajax({
        url: '/update_comments/',
        data: getCommentWithMaxId(),
        type: 'GET',
        dataType: 'html',
        success: function (html) {
            if(html != '') {
                var replyForm = $('#replyForm');
                var currentId = replyForm.parent().children('.comment').attr('id');
                $('#comments').replaceWith(html);
                $('.comment#' + currentId.toString()).parent().append(replyForm);
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
//    alert($("href[id^='reply_to_']"));
//    alert(x.toString() + " # " + y.toString());
//    var currentId = $('.comment').first().attr('id');
//    console.log(currentId);
//    placeForm();
//    updateComments(false);
        $('#commentForm').toggle();
        return false;
    })
}

function getCommentWithMaxId() {
    var maxComment = {id: -1,
                      ref_type: -1,
                      ref_id: -1}
    var id;
    $('.comment, .reply').each(function() {
        id = parseInt( $(this).attr('id') );
        if (id > maxComment.id) {
            maxComment.id = id;
            maxComment.ref_type= $(this).closest('[data-ref_type]').attr('data-ref_type');
            maxComment.ref_id = $(this).closest('[data-ref_id]').attr('data-ref_id');
        }
    })
    return(maxComment);
}
