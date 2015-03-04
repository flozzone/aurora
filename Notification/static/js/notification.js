function notifications_loaded() {
    $('#read_all_button').click(read_all_button_clicked);
	$('#notifications-li').addClass('uRhere');
	window.document.title="Aurora: Notifications"
}

$(notifications_loaded);

function read_all_button_clicked(event) {
    $.get(READ_URL, function (data) {
        location.reload();
    });
}