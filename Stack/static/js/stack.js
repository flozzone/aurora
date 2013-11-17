$(stack_loaded);

function stack_loaded() {
    $(".challenge").click(challenge_clicked);
}

function challenge_clicked(event) {
    var challenge = $(event.target).closest(".challenge");
    if (challenge.hasClass("inactive")) { // TODO: This is very insecure because you can simply add the class to the div
        return
    }
    var challenge_id = challenge.attr('id');
    var url = './get_challenge?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        window.history.pushState('', '', './challenge?id=' + challenge_id);
    });
}
