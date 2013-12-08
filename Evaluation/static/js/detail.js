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
    $(".paginator_others").click(function(event) {
        var url = '/others?page=' + $(event.target).attr('id');
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
        var data = {
            elaboration_id: $(event.target).attr('id'),
            evaluation_text: $(".evaluation").text(),
            evaluation_points: $(".points").text()
        };
        var args = { type: "POST", url: "/submit_evaluation/", data: data,
            error: function () {
                alert('error submitting evaluation');
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
    var data = {
        elaboration_id: elaboration_id,
        evaluation_text: $(".evaluation").text().replace(/\n|<.*?>/g,' '),
        evaluation_points: $.trim($(".points").text())
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