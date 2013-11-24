$(function() {
   $(".submission").click(function(event) {
       var challenge = $(event.target);
       var challenge_id = challenge.attr('id');

       var url = '/submission?challenge_id=' + challenge_id;
       $.get(url, function (data) {
            $('#detail_area').html(data);
       });
   });
});

$(function() {
   $(".waiting").click(function(event) {
       var url = '/waiting';
       $.get(url, function (data) {
            $('#detail_area').html(data);
       });
   });
});

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
   $(".others").click(function(event) {
       var url = '/others?elaboration_id=' + $(event.target).attr('id');
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});

$(function() {
   $(".challenge_txt").click(function(event) {
       var url = '/challenge_txt?elaboration_id=' + $(event.target).attr('id');
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
   });
});