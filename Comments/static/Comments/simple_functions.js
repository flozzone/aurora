/**
 * Created by dan on 1/29/14.
 *
 * simple functions should include modifications, that are done via single click
 * e.g. vote up/down, promote, bookmark
 */

function sendPromotion(comment_number, value) {
    $.ajax({
        url: '/promote_comment/',
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
        sendPromotion(comment_number, true);

        $(this).off();
        $(this).click( demote );
        $(this).toggleClass('comment_demote comment_promote');
        $(this).html('1');

        return false
    }

    function demote(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendPromotion(comment_number, false);

        $(this).off();
        $(this).click( promote );
        $(this).toggleClass('comment_demote comment_promote');
        $(this).html('0');

        return false;
    }
}
