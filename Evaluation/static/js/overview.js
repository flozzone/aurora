$(function() {
	$('.course_selected').addClass('irrelevant');
	$('#evaluation-li').addClass('uRhere');
});


function update_overview(data) {
    data = JSON.parse(data);
    $('#menu').html(data['menu_html']);
    $('#overview').html(data['overview_html']);
}

$(function() {
	$(".mfield").click(function(event) {
		$(".mitem").removeClass('stabilosiert');
		
	});
});

$(function() {
	$(".missing_reviews").click(function(event) {
		loadWait();
		var url = '/overview?data=missing_reviews';
		$.get(url, function (data) {
            update_overview(data);
		});
	});
});

$(function() {
   $(".non_adequate_work").click(function(event) {
		loadWait();
       var url = '/overview?data=non_adequate_work';
       $.get(url, function (data) {
            update_overview(data);
       });
   });
});

$(function() {
   $(".top_level_challenges").click(function(event) {
		loadWait();
       var url = '/overview?data=top_level_challenges';
       $.get(url, function (data) {
            update_overview(data);
       });
   });
});

$(function() {
   $(".complaints").click(function(event) {
		loadWait();
       var url = '/overview?data=complaints';
       $.get(url, function (data) {
            update_overview(data);
       });
   });
});

$(function() {
   $(".questions").click(function(event) {
		loadWait();
       var url = '/questions/';
       $.get(url, function (data) {
            update_overview(data);
       });
   });
});

$(function() {
   $(".evaluated_non_adequate_work").click(function(event) {
	   loadWait();
	   var url = '/overview?data=evaluated_non_adequate_work';
       $.get(url, function (data) {
            update_overview(data);
       });
   });
});

$(function() {
   $(".awesome").click(function(event) {
       var url = '/overview?data=awesome';
       $.get(url, function (data) {
            update_overview(data);
       });
   });
});

$(function() {
   $(".select_challenge").click(function(event) {
       loadWait();
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
       loadWait();
       var url = '/overview?data=awesome';
       $.get(url, function (data) {
            update_overview(data);
       });
   });
});

function load_details(id) {
   var url = '/detail?elaboration_id=' + id;
   $.get(url, function (data) {
       $('#detail_area').html(data);
   });
}

function loadWait() {
	$('.loading_animation').show();
	$('.overview_table').hide();
}

function hideWait() {
	$('.loading_animation').hide();
	$('.overview_table').show();
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
