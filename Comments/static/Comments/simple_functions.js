/**
 * Created by dan on 1/29/14.
 *
 * simple functions should include modifications, that are done via single click
 * e.g. vote up/down, promote, bookmark
 */

function sendValueForComment(url, comment_number, value) { $.ajax({
        url: url,
        data: {comment_id: comment_number,
               value: value},
        type: 'POST',
        dataType: 'json',
        beforeSend: function(xhr, settings) {
            var csrftoken = getCsrfToken();
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    })
}

function registerPromoteLinksForCommentList($comment_list) {
    $comment_list.find('.comment_promote').click( promote );
    $comment_list.find('.comment_demote').click( demote );

    function promote(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendValueForComment('/promote_comment/', comment_number, true);

        $(this).off();
        $(this).click( demote );
        $(this).toggleClass('comment_demote comment_promote');
        $(this).html('1');

        return false
    }

    function demote(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendValueForComment('/promote_comment/', comment_number, false);

        $(this).off();
        $(this).click( promote );
        $(this).toggleClass('comment_demote comment_promote');
        $(this).html('0');

        return false;
    }
}

function registerBookmarkLinksForCommentList($comment_list) {
    $comment_list.find('.comment_bookmark').click( bookmark );
    $comment_list.find('.comment_unbookmark').click( unbookmark );

    var url = '/bookmark_comment/';

    function bookmark(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendValueForComment(url, comment_number, true);

        $(this).off();
        $(this).click( unbookmark );
        $(this).toggleClass('comment_unbookmark comment_bookmark');
        $(this).text('unsave');

        return false;
    }

    function unbookmark(event){
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendValueForComment(url, comment_number, false);
        console.log(comment_number);

        $(this).off();
        $(this).click( bookmark );
        $(this).toggleClass('comment_unbookmark comment_bookmark');
        $(this).text('save');

        return false;
    }
}
