/**
 * Created by dan on 12/21/13.
 */

function post_comment() {
//    var response;

    $.ajax({
        url: "post_comment",
        // the data to send (will be converted to a query string)
        data: {
            id: 123
        },
        // whether this is a POST or GET request
        type: "POST",
        // the type of data we expect back
        dataType: "json",
        success: function (json) {
            $("<h1/>").text("Yay").appendTo("body");
            alert(json);
//            $("<div class=\"content\"/>").html(json.html).appendTo("body");
//            $("<div class=\"content\"/>").html(json.html).appendTo("body");
        },
        error: function (xhr, status) {
            alert("Sorry, there was a problem!");
        },
        complete: function (xhr, status) {
            alert("Request completed successfully");
        }
    });

//    console.log(response); // undefined
}
