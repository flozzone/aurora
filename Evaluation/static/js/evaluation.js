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
       alert("hallo");
   });
});

$(function() {
   $(".non_adequate_reviews").click(function(event) {
       alert("hallo");
   });
});

$(function() {
   $(".top_level_challenges").click(function(event) {
       alert("hallo");
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