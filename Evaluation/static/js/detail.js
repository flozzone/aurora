$(function () {
    $(".review_answer").each(function () {
        this.style.height = (this.scrollHeight+5)+'px';
    });
});

$(function() {
    tinymce.init({
        // selector: "textarea#editor",
		plugins: "wordcount",
		mode : "exact",
		elements :"editor_detail",
		menubar: false,
		statusbar: true,
		toolbar: false,
		height:400,
		readonly: 1
    });
});

$(function() {
   $(".back").click(function(event) {
	   $(".back").text(": : LOADING : :")
   });
});

$(function() {
   $(".stack").click(function(event) {
       var url = './stack';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
   $(".others").click(function(event) {
        var url = './others';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
   $(".challenge_txt").click(function(event) {
       var url = './challenge_txt';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
   $(".similarities").click(function(event) {
       var url = './similarities';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
    $(".paginator").click(function(event) {
        var url = './detail?elaboration_id=' + $(event.target).attr('id');
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
        var data = {
            elaboration_id: $(event.target).attr('id'),
            evaluation_text: $(".evaluation").html(),
            evaluation_points: points
        };
        var args = { type: "POST", url: "./submit_evaluation/", data: data,
            error: function () {
                alert('error submitting evaluation');
            },
            success: function () {
                var next = $(event.target).attr('next');
                if(next == 'None')
                    next = $(event.target).attr('id');
                var url = './detail?elaboration_id=' + next;
                $.get(url, function (data) {
                    $('body').html(data);
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
        var args = { type: "POST", url: "./reopen_evaluation/", data: data,
            success: function () {
                var url = './detail?elaboration_id=' + $(event.target).attr('id');
                $.get(url, function (data) {
                    $('body').html(data);
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
    var args = { type: "POST", url: "./set_appraisal/", data: data,
        error: function () {
            alert('error updating appraisal');
        }
    };
    $.ajax(args);
}

var timer = 0;

function StartEvaluation(elaboration_id) {
    var url = './start_evaluation?elaboration_id=' + elaboration_id;
    $.get(url, function (state) {
        if (state == 'init') {
            $('.evaluation').html("");
            $('.points').attr('contentEditable', true);
        }
        if (state == 'open') {
            $('.evaluation').attr('contentEditable', true);
            $('.points').attr('contentEditable', true);
        }
        if (state.indexOf('locked') > -1) {
            $('.evaluation').html("<div class='evaluation_lock'>" + state + "</div>")
            $('.evaluation').attr('contentEditable', false);
            $('.points').attr('contentEditable', false);
        }
    });
}

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
        evaluation_text: $(".evaluation").html(),
        evaluation_points: points
    };
    var args = { type: "POST", url: "./save_evaluation/", data: data,
        error: function () {
            alert('error saving evaluation');
        }
    };
    $.ajax(args);
}

function load_reviews(elaboration_id) {
   var url = './load_reviews?elaboration_id=' + elaboration_id;
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
        url: "./review_answer/",
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
        var url = './reviewlist';
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
   $(".tag_input").click(function(event) {
       event.stopPropagation();
   });
});

$(function() {
   $(".add_tags_btn").click(function(event) {
       event.stopPropagation();
       var text = $(".tag_input").text();
       var user_id = $(".tag_input").attr('user_id');
       var data = {
                text: text,
                user_id: user_id
            };
       var args = { type: "POST", url: "./add_tags/", data: data,
           success: function (data) {
               $(".tags").html(data);
               $(".tag_input").text("");
           }
       };
       $.ajax(args);
   });
});

$(function() {
   $(".tag").click(function(event) {
       event.stopPropagation();
   });
});

$(function() {
   $(".tag_remove").click(function(event) {
       event.stopPropagation();
       var tag = $(this).attr('name');
       var user_id = $(this).attr('user_id');
       var data = {
                tag: tag,
                user_id: user_id
            };
       var args = { type: "POST", url: "./remove_tag/", data: data,
           success: function (data) {
                $(".tags").html(data);
           }
       };
       $.ajax(args);
   });
});