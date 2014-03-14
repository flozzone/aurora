// making jquery work with django csrf protection.
// see: https://docs.djangoproject.com/en/1.4/ref/contrib/csrf/#ajax

$(function() {
	$('.course_selected').removeClass('irrelevant');
	$('#slides-li').addClass('uRhere');
	window.document.title="Aurora: Slides"
});




var csrftoken = getCookie('csrftoken');

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
// end of csrf stuff.


// takes care of marking slides as confusing/important/
function markSlide(button_div, url) {
    console.log("marking slide: " + url)
    var marker_button = $(button_div);
    var img_src = marker_button.children("img").attr("src");
    // we know that the user has previously clicked on the marker if the
    // src of the button-image contains '_slide_marked'. e.g.: important_slide_marked.png
    var new_value = (img_src.indexOf("_slide_marked") != -1) ? false : true;
    url = url.replace("xxx", String(new_value));
    $.post(url, {}, function(json_return_dict){
        if (json_return_dict.success) {
            if (new_value) {
                var new_img_src = img_src.substring(0, img_src.length - 4) + "_slide_marked.png";
                marker_button.children("img").attr("src", new_img_src);
                if (marker_button.hasClass("nobody")) {
                    marker_button.addClass("somebody");
                    marker_button.removeClass("nobody");
                }
            } else {
                var new_img_src = img_src.substring(0, img_src.length - 17) + ".png";
                marker_button.children("img").attr("src", new_img_src);
                if (json_return_dict.count == 0) {
                    marker_button.addClass("nobody");
                    marker_button.removeClass("somebody");
                }
            }
            marker_button.attr('title', json_return_dict.new_title)
        }
    }, 'json');
}
