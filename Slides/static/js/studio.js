

var scrollEnded = $.debounce(500, false, function () {
    setTimeout(checkSlidesInView, 1000);
});


function checkSlidesInView() {
    var window_position_left = $("#contentblock").scrollLeft();
    var content_width = $("table").width();
    var window_width = $("#contentblock").width();
    var slide_width = $("table tbody tr td").outerWidth(true);
    var table_offset = 10;
    if (slide_width > 0) {
        var first_slide = Math.floor( Math.abs( (window_position_left - table_offset) / slide_width));
        var last_slide = Math.floor( Math.abs( (window_position_left + window_width - table_offset) / slide_width));
        var slide, slide_id;
        //var render_slides_url = base_url + "slidecasting/ajax_render_comments/";

        COMMENTS.setActivePollingObjects(first_slide + 1, last_slide + 1);
        for (var i=first_slide; i<=last_slide; i++ ) {
            /* TODO: insert loading of comments here.
                     * ich hab den alten code da gelassen. das erste ist eine abfrage obs schon 
                       kommentare gibt, das muss natuerlich auch in der neuen variante passieren-
                     * die ids fuer die slides holt dir das ding schon raus.
                     * wenn du noch fragen hast, meld dich einfach.
            */
            // for every slide...
            slide = $($("table tbody tr td")[i]);
            slide_id = slide.attr("id").split("_")[1];
            console.log("loading comments for slide with id: " + slide_id);
            /*
            if (slide.children(".header_comments").length == 0 && slide.children(".loading_circle_image").length == 0) {
                slide.append("<img class='loading_circle_image' src='" + loading_circle_image + "'>");                
                $.post(render_slides_url + slide_id + "/", {}, function(json_response){
                    $("#slide_" + json_response.slide_id).children(".loading_circle_image").remove();
                    $("#lazyload_" + json_response.slide_id).remove();
                    $("#slide_" + json_response.slide_id).append(json_response.rendered_comments);
                }, 'json');
            }
            */
        }
    }
}


function loadAllComments() {
    if (!$("#load_all_comments").hasClass("b_inactive")) {
        //var render_slides_url = base_url + "slidecasting/ajax_render_comments/";
        var slides = $("#slides_table").find("td");
        var slide, slide_id;
        for (var i=0; i < slides.length; i++) {
            /* TODO: insert loading of ALL THE comments here. it's pretty much the same as above.
             */
            slide = $(slides[i]);
            slide_id = slide.attr("id").split("_")[1];
            console.log("loading comments for slide with id: " + slide_id);
            /*
            if (slide.children(".header_comments").length == 0 && slide.children(".loading_circle_image").length == 0) {
                slide.append("<img class='loading_circle_image' src='" + loading_circle_image + "'>");                
                $.post(render_slides_url + slide_id + "/", {}, function(json_response){
                    $("#slide_" + json_response.slide_id).children(".loading_circle_image").remove();
                    $("#lazyload_" + json_response.slide_id).remove();
                    $("#slide_" + json_response.slide_id).append(json_response.rendered_comments);
                    }, 'json');
                }  
            }
            */
        }
        $("#load_all_comments").addClass("b_inactive");
    }
}
