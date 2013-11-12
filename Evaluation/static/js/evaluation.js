$(function() {
    $("#search_challenge").autocomplete({
        source: "/autocomplete_challenge/",
        minLength: 2
//        display search results in results div
//        open: function() {
//            $(this).autocomplete("widget")
//                       .appendTo("#results")
//                       .css("position", "static");
//
//        }
    });
});

$(function() {
   $("#challenge_form").submit(function(event) {
        $.ajax({
           data: $(this).serialize(),
           url: "/search",
            success: function(response) {
                $("#results").html(response);
                results_loaded();
            },
            error: function() {
                alert("error fetching data");
            }
        });
        event.preventDefault();
    });
});

function results_loaded() {
    $(".result").click(function(event) {
        var result = $(event.target).closest(".result");
        var result_id = result.attr('id');
//        $("#details").html(result_id);

        var url = '/submission?id=' + result_id;
        $.get(url, function (data) {
            $('#details').html(data);
        });
    });
}


$(function() {
    $("#search_stack").autocomplete({
        source: "/autocomplete_stack/",
        minLength: 2
    });
});

$(function() {
   $("#stack_form").submit(function(event) {
        $.ajax({
           data: $(this).serialize(),
           url: "/search",
            success: function(response) {
                $("#results").html(response);
                results_loaded();
            },
            error: function() {
                alert("error fetching data");
            }
        });
        event.preventDefault();
    });
});


$(function() {
    $("#search_user").autocomplete({
        source: "/autocomplete_user/",
        minLength: 2
    });
});

$(function() {
   $("#user_form").submit(function(event) {
        $.ajax({
           data: $(this).serialize(),
           url: "/search",
            success: function(response) {
                $("#results").html(response);
                results_loaded();
            },
            error: function() {
                alert("error fetching data");
            }
        });
        event.preventDefault();
    });
});