$(function() {
   $(".missing_reviews").click(function(event) {
       var url = '/update_overview?data=missing_reviews';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

$(function() {
   $(".non_adquate_work").click(function(event) {
       var url = '/update_overview?data=non_adequate_work';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

$(function() {
   $(".non_adequate_reviews").click(function(event) {
       alert("hallo");
   });
});

$(function() {
   $(".top_level_challenges").click(function(event) {
       var url = '/update_overview?data=top_level_challenges';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

$(function() {
   $(".complaints").click(function(event) {
       alert("hallo");
   });
});

$(function() {
   $(".questions").click(function(event) {
       alert("hallo");
   });
});

$(function() {
   $(".select_challenged").click(function(event) {
       alert("hallo");
   });
});

$(function() {
   $(".search").click(function(event) {
       alert("hallo");
   });
});

$(function() {
   $(".tags").click(function(event) {
       alert("hallo");
   });
});

function load_details(id) {
   var url = '/detail?elaboration_id=' + id;
   $.get(url, function (data) {
       $('#detail_area').html(data);
   });
}

$(function() {
    $(".paginator").click(function(event) {
        var url = '/detail?elaboration_id=' + $(event.target).attr('id');
        $.get(url, function (data) {
            $('#detail_area').html(data);
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
   $(".save_evaluation").click(function(event) {
        event.preventDefault();
        var data = {
            elaboration_id: $(event.target).attr('id'),
            evaluation_text: $(".evaluation").text(),
            evaluation_points: $(".points").text()
        };
        var args = { type: "POST", url: "/save_evaluation/", data: data,
            error: function () {
                alert('error saving evaluation');
            }
        };
        $.ajax(args);
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