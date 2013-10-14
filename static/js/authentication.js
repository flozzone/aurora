$(homepage_loaded);

function homepage_loaded() {
    $('#button_sign_in').click(sign_in);
    $('#button_sign_out').click(sign_out);
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
    console.log({
            'username': username,
            'password': password,
            'remember': remember
        });

    $.post("signin/",
        {
            'username': username,
            'password': password,
            'remember': remember
        }).done(function (data) {
        if (data.success === true) {
            location.reload();
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
    $.get("signout/").done(function (data) {
        location.reload();
    });
    return false;
}