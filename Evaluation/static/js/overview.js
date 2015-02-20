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
   $(".select_challenge").click(function(event) {
       loadWait();
	   var url = './select_challenge';
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
       $(".search_user").autocomplete( "search", "" );
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
   $(".search_tag").click(function(event) {
       $(".search_tag").autocomplete( "search", "" );
       $(".search_tag").html("");
   });
});

$(function() {
   $(".search_tag").focusout(function(event) {
       if($('.search_tag').text() == "")
          $(".search_tag").html("tag...");
   });
});

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
        source: "./autocomplete_challenge/",
        select: function (event, ui) {
            var data = {
                selected_challenge: ui.item.value,     // select value from autocomplete box
                selected_user: $('.search_user').text(),
                selected_tag: $('.search_tag').text()
            };
            var args = { type: "POST", url: "./select_challenge/", data: data,
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
        source: "./autocomplete_user/",
        select: function (event, ui) {
           var data = {
                selected_user: ui.item.value     // select value from autocomplete box
           };
           var args = { type: "POST", url: "./select_user/", data: data,
                error: function () {
                    alert('user not found');
                },
                success: function(data) {
                    $('#overview').html(data);
                }
           };
           $.ajax(args);
        },
        minLength: 2
    });
});

$(function() {
    $("#search_tag").autocomplete({
        source: "./autocomplete_tag/",
        select: function (event, ui) {
           // alert("todo: query");
        },
        minLength: 0
    });
});

function sort(param) {
   var url = './sort?data=' + param;
   $.get(url, function (data) {
       update_overview(data);
   });
}