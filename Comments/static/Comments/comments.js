/**
 * Created by dan on 12/21/13.
 */


var purgsLoadFilter;

if (typeof(loadFilter) === 'undefined') {
    purgsLoadFilter = function () {
    };
} else {
    purgsLoadFilter = loadFilter;
}

var COMMENTS = (function (my, $, purgsLoadFilter) {
    "use strict";

    my.registerAllTheElements = function () {
        my.registerStartPolling();
        my.registerStopPolling();

        $('.comment_list').each(function () {
            $(this).find('*').off();
            my.registerElementsForCommentList($(this));
        });

        my.registerReplyButton();
        my.registerCancelReplyButton();

        my.registerAddCommentFormButtons();
        my.registerSubmitCommentButton();
        my.registerCancelCommentButton();

        my.registerPolling();
    };

    my.state = {
        modifying: false,
        posting: false
    };

    my.registerElementsForCommentList = function ($comment_list) {
        my.registerReplyLinksForCommentList($comment_list);
        my.registerEditLinksForCommentList($comment_list);
        my.registerDeleteLinksForCommentList($comment_list);
        my.registerVoteForCommentList($comment_list);
        my.registerPromoteLinksForCommentList($comment_list);
//    registerBookmarkLinksForCommentList($comment_list);
        my.Bookmarks.registerForCommentList($comment_list);
    };

    my.registerPolling = function () {
        var $window = $(window);
        $window.off('blur');
        $window.blur(function () {
            my.POLLING.current_interval = my.POLLING.idle_interval;
        });
        $window.off('focus');
        $window.focus(function () {
            my.POLLING.current_interval = my.POLLING.active_interval;

            if (!my.state.modifying && !my.state.posting) {
                my.startPolling();
            }
        });
    };

    my.registerStopPolling = function () {
        var $stopPolling = $('#stopPolling');
        $stopPolling.off();
        $stopPolling.click(function (event) {
            event.preventDefault();
            my.stopPolling();
            return false;
        });
    };

    my.registerStartPolling = function () {
        var $startPolling = $('#startPolling');
        $startPolling.off();
        $startPolling.click(function (event) {
            event.preventDefault();
            my.startPolling();
            return false;
        });
    };

    my.registerVoteForCommentList = function ($comment_list) {
        $comment_list.find('.vote_up_on').click(function (event) {
            event.preventDefault();

            my.POLLING.resetTimer();
            vote($(this), 'up', 1);

            return false;
        });

        $comment_list.find('.vote_down_on').click(function (event) {
            event.preventDefault();

            my.POLLING.resetTimer();
            vote($(this), 'down', -1);

            return false;
        });

        function vote($link, direction, scorediff) {
            var $parent = $link.parent();
            var classname = direction + 'voted';
            var oppositeClass;

            if (direction === 'up') {
                oppositeClass = 'downvoted';
            } else {
                oppositeClass = 'upvoted';
            }

            if ($parent.hasClass(classname)) {
                return false;
            }

            if ($parent.hasClass(oppositeClass)) {
                $parent.removeClass(oppositeClass);
            } else {
                $parent.addClass(classname);
            }

            $parent.find(oppositeClass);


            var $score = $parent.find('.comment_score_value');
            var newscore = +$score.html() + scorediff;
            if (newscore > 0) {
                newscore = '+' + newscore.toString();
            }
            $score.html(newscore);

            var url = my.VOTE_URL;
            var data = {
                direction: direction,
                comment_id: $link.data('comment_number')
            };

            my.post(url, data);
        }
    };

    my.registerAddCommentFormButtons = function () {
        $('.button_add_comment_form').each(function () {
            my.registerAddCommentFormButton($(this));
        });
    };

    my.registerAddCommentFormButton = function ($button) {
        $button.off();
        $button.click(function (event) {
            event.preventDefault();

            if (my.state.modifying) {
                return false;
            }
            my.state.posting = true;

            my.stopPolling();
            var $replyForm = $('#replyForm');
            $replyForm.hide();

            var ref_id = $(this).data('ref_id');
            var ref_type = $(this).data('ref_type');
            var $commentForm = $('#commentForm');
            $commentForm.find('#id_reference_id').val(ref_id);
            $commentForm.find('#id_reference_type_id').val(ref_type);

            var comment_list_uri = location.pathname + location.search;
            $commentForm.find('#id_uri').val(comment_list_uri);

            if ($commentForm.is(':visible')) {
                $commentForm.prev().show();
            }
            $(this).after($commentForm);
            var reply_text = $replyForm.find('textarea').val();
            if (reply_text !== '') {
                reply_text = reply_text.replace(/(@[^ ]+\s|^)/, '');
                $commentForm.find('textarea').val(reply_text);
            }
            $commentForm.show();
            $(this).hide();

            return false;
        });
    };

    my.registerEditLinksForCommentList = function ($comment_list) {
        $comment_list.find('.edit_link').click(function (event) {
            event.preventDefault();

            if (my.state.posting || my.state.modifying) {
                return false;
            }
            my.state.modifying = true;

            var $editButtons = $('#edit_buttons');

            my.stopPolling();

            var $comment = $(this).closest('.comment, .response');
            var $commentText = $comment.find('.comment_text, .response_text');
            var $actions = $(this).closest('.comment_actions, .response_actions');
            var oldCommentText = $commentText.html();

            $commentText.attr('contenteditable', true);

            $comment.on("keydown", function (e) {
                var lineBreak;

                if (e.which === 13 && !e.shiftKey) {
                    e.preventDefault();

                    lineBreak = "<br />&nbsp";
                    document.execCommand("insertHTML", false, lineBreak);
                    document.execCommand("delete");

                    return false;
                }
            });

            $(document).keydown(handleHotkeys);
            function handleHotkeys(e) {
                if (e.which === 27) {
                    cancelEdit(e);
                }
                if (e.which === 13 && e.shiftKey) {
                    saveEdit(e);
                }
            }

            $actions.after($editButtons);
            $actions.hide();
            $editButtons.show();

            function endEdit() {
                $actions.show();
                $('#element_shelter').append($editButtons);
                $editButtons.hide();
                $commentText.attr('contenteditable', false);

                $(document).off('keydown', handleHotkeys);
                my.state.modifying = false;
                my.startPolling();
            }

            var $cancel = $('#edit_cancel');
            $cancel.off();
            $cancel.click(cancelEdit);
            function cancelEdit(event) {
                event.preventDefault();

                $commentText.html(oldCommentText);

                endEdit();

                return false;
            }

            var $save = $('#edit_save');
            $save.off();
            $save.click(saveEdit);
            function saveEdit(event) {
                event.preventDefault();

                var text = $commentText.html().trim()
                    .replace(/<br(\s*)\/*>/ig, '\n') // replace single line-breaks
                    .replace(/&nbsp;?/ig, ' ')
                    .replace(/&lt;?/ig, '<')
                    .replace(/&gt;?/ig, '>')
                    .replace(/&amp;?/ig, '&');

                var data = {comment_id: $comment.data('comment_number'),
                    text: text};

                $.ajax({
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader("X-CSRFToken", my.getCsrfToken());
                    },
                    url: my.EDIT_URL,
                    crossDomain: false,
                    data: data,
                    type: 'POST',
                    dataType: 'html',
                    success: function () {
                        endEdit();
                    },
                    complete: function (xhr, status) {
                    }
                });

                return false;
            }

            return false;
        });
    };

    my.registerReplyLinksForCommentList = function ($comment_list) {
        $comment_list.find('[id^=reply_comment_link_]').click(function (event) {
            event.preventDefault();

            if (my.state.modifying) {
                return false;
            }
            my.state.posting = true;

            my.stopPolling();

            var $replyForm = $('#replyForm');
            var new_text;

            var comment_number = $(this).data('reply_to');
            my.setCommentId($replyForm, comment_number);

            var uri = location.pathname + location.search;
            $replyForm.find('#id_uri').val(uri);

            var user = $(this).closest('.comment, .response').data('comment_author');

            var $commentTextarea = $('#commentTextarea');
            var $replyTextarea = $('#replyTextarea');
            if ($commentTextarea.val() !== '') {
                new_text = $commentTextarea.val();
            } else {
                new_text = $replyTextarea.val();
            }
            new_text = new_text.replace(/(@[^ ]+\s|^)/, '@' + user + ' ');
            $replyTextarea.val(new_text);

            $(this).after($replyForm);
            my.hideCommentForm();
            $replyForm.show();
            return false;
        });
    };

    my.setCommentId = function ($form, comment_number) {
        $form.find('#id_parent_comment').attr('value', comment_number);

        var $comment = $('[data-comment_number=' + comment_number + ']');
        var ref_obj = my.findClosestRefObj($comment);
        $form.find('#id_reference_id').attr('value', ref_obj.id);
        $form.find('#id_reference_type_id').attr('value', ref_obj.type);
    };

    my.registerDeleteLinksForCommentList = function ($comment_list) {
        $comment_list.find('.delete_comment, .delete_response').click(function (event) {
            event.preventDefault();

            if (my.state.modifying || my.state.posting) {
                return false;
            }

            my.stopPolling();
            my.state.modifying = true;

            var $delete_buttons = $('#delete_buttons');
            var $actions = $(this).closest('.comment_actions, .response_actions');
            $actions.after($delete_buttons);
            $actions.hide();
            $delete_buttons.show();

            var comment_number = $(this).data('delete_id');

            function deleteComment() {
                $.ajax({
                    url: my.DELETE_URL,
                    data: { comment_id: comment_number },
                    type: 'POST',
                    dataType: 'json',
                    beforeSend: function (xhr) {
                        var csrftoken = my.getCsrfToken();
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    },
                    complete: function () {
                        endDelete();
                    }
                });
            }

            function endDelete() {
                $delete_buttons.hide();
                $('#element_shelter').append($delete_buttons);
                my.startPolling();
                my.state.modifying = false;
            }

            var $delete_cancel = $('#delete_cancel');
            $delete_cancel.off();
            $delete_cancel.click(function (event) {
                event.preventDefault();
                endDelete();
                $actions.show();
                return false;
            });

            var $delete_confirm = $('#delete_confirm');
            $delete_confirm.off();
            $delete_confirm.click(function (event) {
                event.preventDefault();
                deleteComment();
                return false;
            });

            return false;
        });
    };

    my.registerReplyButton = function () {
        var $button_post_reply = $('#button_post_reply');
        $button_post_reply.off();
        $button_post_reply.click(function (event) {
            event.preventDefault();

            var $replyTextarea = $('#replyTextarea');
            var text = $replyTextarea.val();
            $replyTextarea.val(text);

            $.ajax({
                url: my.REPLY_URL,
                data: $(this).closest('form').serialize(),
                type: 'POST',
                dataType: 'html',
                success: function () {
                    $('#replyForm').hide();
                    $("#replyTextarea").val('');
                    my.startPolling();
                    my.state.posting = false;
                }
            });
            return false;
        });
    };

    my.registerCancelReplyButton = function () {
        var $button_cancel_reply = $('#button_cancel_reply');
        $button_cancel_reply.off();
        $button_cancel_reply.click(function (event) {
            event.preventDefault();
            $('#replyForm').hide();
            $('#replyTextarea').val('');
            my.state.posting = false;
            my.startPolling();
            return false;
        });
    };

    my.hideCommentForm = function () {
        var $form = $('#commentForm');
        $form.hide();
        $('#commentTextarea').val('');
        $form.prev().show();
    };

    my.registerCancelCommentButton = function () {
        var $button_cancel_comment = $('#button_cancel_comment');
        $button_cancel_comment.off();
        $button_cancel_comment.click(function (event) {
            event.preventDefault();
            my.hideCommentForm();
            my.state.posting = false;
            my.startPolling();
            return false;
        });
    };

    my.registerSubmitCommentButton = function () {
        var $button_add_comment = $('#button_add_comment');
        $button_add_comment.off();
        $button_add_comment.click(function (event) {
            event.preventDefault();

            var $commentTextarea = $("#commentTextarea");
            var text = $commentTextarea.val();
            $commentTextarea.val(text);

            $.ajax({
                url: my.POST_URL,
                data: $("#commentForm").serialize(),
                type: "POST",
                // the type of data we expect back
                dataType: 'html',
                success: function () {
                    my.hideCommentForm();
                    my.startPolling();
                },
                error: function (xhr, status) {
                },
                complete: function (xhr, status) {
                }
            });

            my.state.posting = false;
            return false;
        });
    };

    my.POLLING = {
        stopped: false,
        current_interval: 5000,
        active_interval: 5000,
        idle_interval: 60000,
        increase_interval: function () {
            my.POLLING.current_interval = Math.min(my.POLLING.current_interval * 2, my.POLLING.idle_interval);
        },
        firstRefId: null,
        lastRefId: null,

        resetTimer: function () {
            if (!my.POLLING.stopped) {
                clearTimeout(my.POLLING.current_timeout);
                my.POLLING.current_timeout = setTimeout(function () {
                    my.updateCommentLists(true);
                }, my.POLLING.current_interval);
            }
        }
    };

    my.updateCommentLists = function (keepPolling) {
        var data = {revisions: my.getRevisions()};
		$('#lindicator').fadeIn(50);
        $.ajax({
            url: my.UPDATE_URL,
            data: data,
            type: 'POST',
            dataType: 'json',
            success: function (json) {
                var comment_list_updates = json.comment_list_updates;
                if (comment_list_updates.length > 0) {
                    my.handleCommentListUpdates(comment_list_updates);
                    purgsLoadFilter();
                }
                if (json.polling_active_interval) {
                    my.POLLING.active_interval = json.polling_active_interval;
                }
                if (json.polling_idle_interval) {
                    my.POLLING.idle_interval = json.polling_idle_interval;
                }
            },
            error: function () {
                my.POLLING.increase_interval();
            },
            complete: function () {
                if (keepPolling === true) {
                    my.POLLING.resetTimer();
                }
            },
            beforeSend: function (xhr) {
                var csrftoken = my.getCsrfToken();
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });
		$('#lindicator').fadeOut(200);
    };

    my.findCommentListByRef = function (ref_id, ref_type) {
        return $('.comment_list').filter('[data-ref_type=' + ref_type + ']')
            .filter('[data-ref_id=' + ref_id + ']');
    };

    my.handleCommentListUpdates = function (comment_list_updates) {
        var ref_id, ref_type, html;
        var $comment_list;

        for (var i = 0; i < comment_list_updates.length; i++) {
            ref_id = comment_list_updates[i].ref_id;
            ref_type = comment_list_updates[i].ref_type;
            html = comment_list_updates[i].comment_list;

            $comment_list = my.findCommentListByRef(ref_id, ref_type);
            my.replaceCommentListWithHtml($comment_list, html);
            my.fixEndlessPaginationLinks();
        }
    };

    my.replaceCommentListWithHtml = function ($comment_list, html) {
        var ref_type = $comment_list.data('ref_type');
        var ref_id = $comment_list.data('ref_id');

        // reply form replacement & conservation
        var $replyForm = $comment_list.find('#replyForm');
        if ($replyForm.length > 0) {
            // save current replyForm so it isn't deleted by the div update
            var prev_id = $replyForm.prev().attr('id');
            var parent_comment_number = $comment_list.find('#id_parent_comment').val();
            $comment_list.replaceWith(html);

            var $new_prev = $('#' + prev_id);
            if ($new_prev.length > 0) {
                $new_prev.after($replyForm);
            } else {
                var $parent_comment = $('[data-comment_number=' + parent_comment_number + ']');
                if ($parent_comment > 0) {
                    $parent_comment.append($replyForm);
                } else {
                    $comment_list = my.findCommentListByRef(ref_id, ref_type);
                    $comment_list.prepend($replyForm);
                    $replyForm.hide();
                }
            }

            my.registerReplyButton();
            my.registerCancelReplyButton();
        } else {
            $comment_list.replaceWith(html);
        }

        // get us the new comment list for the ref_object
        $comment_list = my.findCommentListByRef(ref_id, ref_type);

        // only reregister replaced elements to avoid multi registration
        my.registerElementsForCommentList($comment_list);
    };

    my.stopPolling = function () {
        clearTimeout(my.POLLING.current_timeout);
        my.POLLING.stopped = true;
    };

    my.startPolling = function () {
        my.POLLING.stopped = false;
        my.updateCommentLists(true);
    };

    my.setActivePollingObjects = function (firstRefId, lastRefId) {
        my.POLLING.firstRefId = firstRefId;
        my.POLLING.lastRefId = lastRefId;

        my.updateCommentLists(false);
    };

    my.getRevisions = function () {
        var revisions = [];
        var ref_id;

        var $comment_lists = $('.comment_list');
        $comment_lists.each(function () {
            var $this = $(this);
            ref_id = $this.attr('data-ref_id');
            if (my.POLLING.firstRefId !== null) {
                if (ref_id < my.POLLING.firstRefId || ref_id > my.POLLING.lastRefId) {
                    return true;
                }
            }

            revisions.push({
                number: $this.data('revision'),
                ref_type: $this.data('ref_type'),
                ref_id: ref_id
            });

            return true;
        });

        return revisions;
    };

    my.getRevision = function ($comment_list) {
        return {
            id: $comment_list.data('revision'),
            ref_type: $comment_list.data('ref_type'),
            ref_id: $comment_list.data('ref_id')
        };
    };

    my.findClosestRefObj = function ($child) {
        var ref_type = $child.closest('[data-ref_type]').attr('data-ref_type');
        var ref_id = $child.closest('[data-ref_id]').attr('data-ref_id');
        return { type: ref_type, id: ref_id };
    };

    /**
     * Rewrites the endless pagination link to a correct value for updating a single comment list
     */
    my.fixEndlessPaginationLinks = function() {
        $(".endless_more").each(function() {
            var $this = $(this);
            var refObj = my.findClosestRefObj($this),
                refId = refObj.id.toString(10),
                refType = refObj.type.toString(10);
            var href = $this.attr('href');
            var new_link = "/comment_list_page/?ref_id=" + refId + "&ref_type=" + refType + "&";
            var new_href = href.replace(/.*\/\?/, new_link);
            $this.attr('href', new_href);
        });
    };

    $(document).ready(function () {
        my.registerAllTheElements();
        my.fixEndlessPaginationLinks();
    });

    $(window).load(function() {
        if(typeof(checkSlidesInView) !== 'undefined') {
            checkSlidesInView();
        }

        my.startPolling();
    });

    return my;
}(COMMENTS || {}, jQuery, purgsLoadFilter));
