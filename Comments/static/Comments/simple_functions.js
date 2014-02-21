/**
 * Created by dan on 1/29/14.
 *
 * simple functions should include modifications, that are done via single click
 * e.g. vote up/down, promote, bookmark
 */

//"use strict";

// TODO delete
//var holyShit = {
//    polling_interval: 5000,
//    sendValueForComment: function (url, comment_number, value) {
//        this.polling_interval;
//    }
//}

function sendValueForComment(url, comment_number, value) {
    $.ajax({
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
        $(this).find('i').toggleClass('gold ungold');

        return false;
    }

    function demote(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendValueForComment('/promote_comment/', comment_number, false);

        $(this).off();
        $(this).click( promote );
        $(this).toggleClass('comment_demote comment_promote');
        $(this).find('i').toggleClass('gold ungold');

        return false;
    }
}

// TODO chose one implementation for bookmarks, delete the other :)
var Bookmarks = {
    url: '/bookmark_comment/',

    registerForCommentList: function ($comment_list) {
        var that = this;
        $comment_list.find('.comment_bookmark').click(function (event) { that.bookmark(event, $(this)) });
        $comment_list.find('.comment_unbookmark').click(function (event) { that.unbookmark(event, $(this)) });
    },

    bookmark: function (event, $link) {
        event.preventDefault();

        var comment_number = $link.attr('data-comment_number');
        sendValueForComment(this.url, comment_number, true);

        var that = this;
        $link.off();
        $link.click(function(event) { that.unbookmark(event, $link) });
        $link.toggleClass('comment_unbookmark comment_bookmark');
        $link.text('unbookmark');

        return false;
    },

    unbookmark: function (event, $link) {
        event.preventDefault();

        var comment_number = $link.attr('data-comment_number');
        sendValueForComment(this.url, comment_number, false);

        var that = this;
        $link.off();
        $link.click(function(event) { that.bookmark(event, $link) });
        $link.toggleClass('comment_unbookmark comment_bookmark');
        $link.text('bookmark');

        return false;
    }
};

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
        $(this).text('unbookmark');

        return false;
    }

    function unbookmark(event) {
        event.preventDefault();

        var comment_number = $(this).attr('data-comment_number');
        sendValueForComment(url, comment_number, false);

        $(this).off();
        $(this).click( bookmark );
        $(this).toggleClass('comment_unbookmark comment_bookmark');
        $(this).text('bookmark');

        return false;
    }
}