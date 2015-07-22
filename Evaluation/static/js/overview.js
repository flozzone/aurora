$(function() {
	$('#evaluation-li').addClass('uRhere');
});

function update_overview(data) {
    data = JSON.parse(data);
    $('#menu').html(data['menu_html']);
    $('#overview').html(data['overview_html']);
    window.location.href = "./";
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
       if($('.search_challenge').text() == "") {
           $(".search_challenge").html("task...");
           search();
       }
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
       if($('.search_user').text() == "") {
           $(".search_user").html("user...");
           search();
       }
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
       if($('.search_tag').text() == "") {
           $(".search_tag").html("tag...");
           search();
       }
   });
});

$(function() {
   $(".remove_sel_challenge_btn").click(function(event) {
        $(".search_challenge").html("task...");
        search();
   });
});

$(function() {
   $(".remove_sel_user_btn").click(function(event) {
        $(".search_user").html("user...");
        search();
   });
});

$(function() {
   $(".remove_sel_tag_btn").click(function(event) {
        $(".search_tag").html("tag...");
        search();
   });
});

function search(challenge, user, tag) {
    if (typeof(challenge)==='undefined') challenge = $('.search_challenge').text();
    if (typeof(user)==='undefined') user = $('.search_user').text();
    if (typeof(tag)==='undefined') tag = $('.search_tag').text();

    if((challenge=="task...") && (user=="user...") && (tag=="tag...")) {
        $('#overview').html("");
    } else {
        var url = "./search/";
        var data = {
                selected_challenge: challenge,
                selected_user: user,
                selected_tag: tag
        };
        var args = { type: "POST", url: url, data: data,
            success: function(data) {
                window.location.href="./";
            }
        };
        $.ajax(args);
    }
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
        source: "./autocomplete_challenge/",
        select: function (event, ui) {
            search(ui.item.value, undefined, undefined);
        },
        minLength: 0
    });
});

$(function() {
    $("#search_user").autocomplete({
        source: "./autocomplete_user/",
        select: function (event, ui) {
            search(undefined, ui.item.value, undefined);
        },
        minLength: 2
    });
});

$(function() {
    $("#search_tag").autocomplete({
        source: "./autocomplete_tag/",
        select: function (event, ui) {
            search(undefined, undefined, ui.item.value);
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