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
       alert("TODO: non_adequate_reviews");
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
       alert("TODO: complaints");
   });
});

$(function() {
   $(".questions").click(function(event) {
       alert("TODO: questions");
   });
});

$(function() {
   $(".select_challenge").click(function(event) {
       var url = '/select_challenge';
       $.get(url, function (data) {
            $('#select_challenge').html(data);
       });
   });
});

$(function() {
   $(".search").click(function(event) {
       alert("TODO: search");
   });
});

$(function() {
   $(".tags").click(function(event) {
       alert("TODO: tags");
   });
});

function load_details(id) {
   var url = '/detail?elaboration_id=' + id;
   $.get(url, function (data) {
       $('#detail_area').html(data);
   });
}

function load_elaborations(id) {
   var url = '/update_overview?data=select_challenge&id=' + id;
   $.get(url, function (data) {
        $('#overview').html(data);
        $('#select_challenge').html('<div class="select_challenge" id="select_challenge">select challenge +</div>');
   });
}