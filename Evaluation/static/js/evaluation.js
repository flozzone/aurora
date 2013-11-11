$(function() {
    $("#search").autocomplete({
        source: "/autocomplete/",
        minLength: 2
        // display search results in results div
//        open: function() {
//            $(this).autocomplete("widget")
//                       .appendTo("#results")
//                       .css("position", "static");
//
//        }
    });
});