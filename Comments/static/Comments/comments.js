/**
 * Created by dan on 12/21/13.
 */
$(document).ready(function() {
});

function postComment() {
    $.ajax({
        url: "/post_comment/",
        data: $("#commentForm").serialize(),
        type: "POST",
        // the type of data we expect back
        dataType: 'html',
        success: function (response) {
            $("#commentText").val('');

            $('#comments').prepend(response)
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

function showReplyForm(that) {
//    look for form
//    if form doesnt exist: create
//    if it does exist: unhide
//    that.append($('<h1/>').text('blub'));
    alert(that.text);
}

function pollForChanges() {
//    $.post('ajax/test.html', function (data) {
//        alert(data);  // process results here
//        setTimeout(pollForChanges(), 5000);
//    });
}

function updateComments() {
    var lastComment = { last_comment_id: getMaxCommentId(), reference_object_id: reference_object_id }
    $.ajax({
        url: '/update_comment/',
        data: lastComment,
        type: 'json',
        success: function (json) {
            alert(json);
//          if we get new stuff update DOM
        }
    })
}

function postReply(id) {
    alert(id);
}

function getMaxCommentId() {
    var max = 0;
    var id;
    $('.comment, .reply').each(function() {
        id = parseInt( $(this).attr('id') );
        if (id > max) max = id;
    })
    return(max);
}
