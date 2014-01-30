/**
 * Created by dan on 1/29/14.
 *
 * simple functions should include modifications, that are done via single click
 * e.g. vote up/down, promote, bookmark
 */

function registerSimpleFunctions() {
    registerPromoteLinks();
}

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

function registerPromoteLinks() {
    $('.comment_promote').click( promote );
    $('.comment_demote').click( demote );

    function promote(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendPromotion(comment_number, true);

        $(this).off();
        $(this).click( demote );
        $(this).toggleClass('comment_demote comment_promote');
        $(this).html('demote comment');

        return false
    }

    function demote(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendPromotion(comment_number, false);

        $(this).off();
        $(this).click( promote );
        $(this).toggleClass('comment_demote comment_promote');
        $(this).html('promote comment');

        return false;
    }
}
