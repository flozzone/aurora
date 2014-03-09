$(homepage_loaded);

function homepage_loaded() {
    $('#button_sign_in').click(sign_in);
    $('#button_sign_out').click(sign_out);
    $('.ct_menu').click(course_change);
    if ($('#unread_notifications').length) {
        notifications_refresh();
    }
} 

function notifications_refresh() {
    (function refresh_worker() {
        $.ajax({
            url: '/notifications/refresh',
            success: function (data) {
                if ($.isNumeric(data)) {
                    $('#unread_notifications').html(data);
                    setTimeout(refresh_worker, 60000);
                }
            }
        });
    })();
}

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

function course_change(event) {
	$('.ct_menu').removeClass('selected');
	$(event.target).addClass('selected');
    ajax_setup();
    var short_title = $(event.target).data('shortname');
    $.post("/course/",
        {
            'short_title': short_title
        }).done(function (data) {
            console.log(data);
            if (data.success === true) {
                console.log(data.success);
                location.href = '/';
            } else {
                console.log("test failed");
                $('#password').val("")
                $('#error_message').html(data.message);
                $('#error').show();
            }
        });
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function ajax_setup() {
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}


function sign_in() {
    ajax_setup();
    var username = $('#username').val();
    var password = $('#password').val();
    var remember = $('#checkbox_remember').prop('checked');
    console.log(next);
    console.log({
        'username': username,
        'password': password,
        'remember': remember
    });

    $.post("/signin/",
        {
            'username': username,
            'password': password,
            'remember': remember
        }).done(function (data) {
            if (data.success === true) {
                location.href = next;
            } else {
                $('#password').val("")
                $('#error_message').html(data.message);
                $('#error').show();
            }
        });
    return false;
}

function sign_out() {
    ajax_setup();
    $.get("/signout/").done(function (data) {
        window.location.href = '/login';
    });
    return false;
}