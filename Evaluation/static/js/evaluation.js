$(function() {
    $("#search").autocomplete({
        source: "/autocomplete/",
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
   $("#search_form").submit(function(event) {
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
    $(".challenge").click(function(event) {
        var challenge = $(event.target);
        var challenge_id = challenge.attr('id');
        $("#details").html(challenge_id);
    });
}