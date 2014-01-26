$(notifications_loaded);

function notifications_loaded() {
    $('#read_all_button').click(read_all_button_clicked);
}

function read_all_button_clicked(event) {
    $.get("/notifications/read", function (data) {
        location.reload();
    });
}