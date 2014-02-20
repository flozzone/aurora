$(function() {
   $(".missing_reviews").click(function(event) {
       var url = '/update_overview?data=missing_reviews';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

$(function() {
   $(".non_adequate_work").click(function(event) {
       var url = '/update_overview?data=non_adequate_work';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

$(function() {
   $(".non_adequate_reviews").click(function(event) {
       var url = '/update_overview?data=non_adequate_reviews';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
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
       var url = '/update_overview?data=non_adequate_reviews';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

$(function() {
   $(".questions").click(function(event) {
       var url = '/questions';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

$(function() {
   $(".evaluated_non_adequate_work").click(function(event) {
       var url = '/update_overview?data=evaluated_non_adequate_work';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
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
   $(".search_challenge").click(function(event) {
       $(".search_challenge").html("");
       $(".search_challenge").autocomplete( "search", "" );
   });
});

$(function() {
   $(".search_challenge").focusout(function(event) {
       if($('.search_challenge').text() == "")
          $(".search_challenge").html("challenge...");
   });
});

$(function() {
   $(".search_user").click(function(event) {
       // $(".search_user").autocomplete( "search", "" );
       $(".search_user").html("");
   });
});

$(function() {
   $(".search_user").focusout(function(event) {
       if($('.search_user').text() == "")
          $(".search_user").html("user...");
   });
});

$(function() {
   $(".search_all").click(function(event) {
       $(".search_all").html("");
   });
});

$(function() {
   $(".search_all").focusout(function(event) {
       if($('.search_all').text() == "")
          $(".search_all").html("all...");
   });
});

$(function() {
   $(".awesome").click(function(event) {
       var url = '/update_overview?data=awesome';
       $.get(url, function (data) {
            $('#overview').html(data);
       });
   });
});

function load_details(id) {
   var url = '/detail?elaboration_id=' + id;
   $.get(url, function (data) {
       $('#detail_area').html(data);
   });
}

$(function() {
    $("#search_challenge").autocomplete({
        source: "/autocomplete_challenge/",
        select: function (event, ui) {
           var data = {
                selected_challenge: ui.item.value     // select value from autocomplete box
           };
           var args = { type: "POST", url: "/select_challenge/", data: data,
                error: function () {
                    alert('challenge not found');
                },
                success: function(data) {
                    $('#overview').html(data);
                }
           };
           $.ajax(args);
        },
        minLength: 0
    });
});

$(function() {
    $("#search_user").autocomplete({
        source: "/autocomplete_user/",
        minLength: 2
    });
});

$(function() {
   $(".search_btn").click(function(event) {
       var data = {
            search_user: $('.search_user').text(),
            search_all: $('.search_all').text()
       };
       var args = { type: "POST", url: "/search/", data: data,
            error: function () {
                alert('no search results found');
            },
            success: function(data) {
                $('#overview').html(data);
            }
       };
       $.ajax(args);
   });
});