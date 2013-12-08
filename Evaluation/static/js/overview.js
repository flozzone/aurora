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
   $(".search_challenge").click(function(event) {
       $(".search_challenge").autocomplete( "search", "" );
   });
});

$(function() {
   $(".search_user").click(function(event) {
       // $(".search_user").autocomplete( "search", "" );
       $(".search_user").html("");
   });
});

$(function() {
   $(".search_all").click(function(event) {
       $(".search_all").html("");
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