$(profile_loaded);

function profile_loaded() {
    $('.save_button').click(save_button_clicked);
}

function save_button_clicked() {
    $('#profile').submit()
}
