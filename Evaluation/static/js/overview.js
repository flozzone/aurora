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