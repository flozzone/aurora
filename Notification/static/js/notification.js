function notifications_loaded() {
    $('#read_all_button').click(read_all_button_clicked);
	$('.course_selected').addClass('irrelevant');
	$('#notifications-li').addClass('uRhere');
}

$(notifications_loaded);

function read_all_button_clicked(event) {
    $.get("/notifications/read", function (data) {
        location.reload();
    });
}