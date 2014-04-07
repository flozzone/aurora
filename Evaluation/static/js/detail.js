$(function() {
    tinymce.init({
        // selector: "textarea#editor",
        mode : "exact",
        elements :"editor_detail",
        menubar: false,
        statusbar: false,
		toolbar: false,
		height:300,
        readonly: 1
    });
});

$(function() {
   $(".back").click(function(event) {
	   $(".back").text(": : LOADING : :")
        var url = '/back';
        $.get(url, function (data) {
            window.location.href = "/evaluation/";
        });
   });
});

$(function() {
   $(".stack").click(function(event) {
       var url = '/stack';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
   $(".others").click(function(event) {
        var url = '/others';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
   $(".challenge_txt").click(function(event) {
       var url = '/challenge_txt';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
    $(".paginator").click(function(event) {
        var url = '/detail?elaboration_id=' + $(event.target).attr('id');
        $.get(url, function (data) {
            $('#detail_area').html(data);
        });
    });
});

$(function() {
   $(".submit_evaluation").click(function(event) {
        event.preventDefault();

        var points = Math.abs(parseInt($(".points").text()) || 0);
        if ($.trim($(".evaluation").text()).length == 0) {
            $(".error").html("you forgot feedback!");
            return;
        }
        if (points == 0) {
            $(".error").html("points must be numeric!");
            return;
        }

        var data = {
            elaboration_id: $(event.target).attr('id'),
            evaluation_text: $(".evaluation").text(),
            evaluation_points: points
        };
        var args = { type: "POST", url: "/submit_evaluation/", data: data,
            error: function () {
                alert('error submitting evaluation');
            },
            success: function () {
                var next = $(event.target).attr('next');
                if(next == 'None')
                    next = $(event.target).attr('id');
                var url = '/detail?elaboration_id=' + next;
                $.get(url, function (data) {
                    $('#detail_area').html(data);
                });
            }
        };
        $.ajax(args);
    });
});

$(function() {
   $(".reopen_evaluation").click(function(event) {
        event.preventDefault();
        var data = {
            elaboration_id: $(event.target).attr('id')
        };
        var args = { type: "POST", url: "/reopen_evaluation/", data: data,
            success: function () {
                var url = '/detail?elaboration_id=' + $(event.target).attr('id');
                $.get(url, function (data) {
                    $('#detail_area').html(data);
                });
            }
        };
        $.ajax(args);
    });
});

function set_appraisal(review_id, appraisal) {
    var data = {
        review_id: review_id,
        appraisal: appraisal
    };
    var args = { type: "POST", url: "/set_appraisal/", data: data,
        error: function () {
            alert('error updating appraisal');
        }
    };
    $.ajax(args);
}

var timer = 0;

function DelayedAutoSave(elaboration_id) {
    if (timer)
        window.clearTimeout(timer);
    timer = window.setTimeout(function() {
        AutoSave(elaboration_id);
    }, 500);
}

function AutoSave(elaboration_id) {
    var points = Math.abs(parseInt($(".points").text()) || 0);
    var data = {
        elaboration_id: elaboration_id,
        evaluation_text: $(".evaluation").text().replace(/\n|<.*?>/g,' '),
        evaluation_points: points
    };
    var args = { type: "POST", url: "/save_evaluation/", data: data,
        error: function () {
            alert('error saving evaluation');
        }
    };
    $.ajax(args);
}

function load_reviews(elaboration_id) {
   var url = '/load_reviews?elaboration_id=' + elaboration_id;
   $.get(url, function (data) {
       $('#info_area').html(data);
   });
}

$(function() {
   $(".review_submit").click(function(event) {
    event.preventDefault();
    var data = {};
    data['answers'] = [];
    var missing_answer = false;
    $(".question_container").each(function (index) {
        var answer_object = $(this).find('.answer');
        var answer = null;
        if (answer_object.hasClass('boolean_answer')) {
            answer = answer_object.find('input:checked')
            if (answer.length === 0) {
                missing_answer = true;
            }
            answer = answer.val();
        } else {
            answer = answer_object.find('#text_answer').val();
        }

        var question = answer_object.parent().find('.question').first();
        var question_id = question.attr('id');
        if (question_id) {
            data['answers'].push({
                'question_id': answer_object.parent().find('.question').first().attr('id'),
                'answer': answer
            });
        }
    });

    var appraisal = $('input[name=appraisal]:checked');
    if (appraisal.length === 0) {
        missing_answer = true
    }

    if (missing_answer) {
        alert("please fill out all answers");
        return;
    }
    data['appraisal'] = appraisal.val();
    ajax_setup()
    var args = {
        type: "POST",
        url: "/evaluation/review_answer/",
        data: JSON.stringify(data),
        error: function (data) {
            alert('error submitting review');
        },
        success: review_submitted
    };
    $.ajax(args);
   });
});

function review_submitted() {
    window.location.href = '../evaluation';
}

$(function() {
   $(".review_list").click(function(event) {
        var url = '/reviewlist';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});