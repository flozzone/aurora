$(stack_loaded);

function stack_loaded() {
    $(".challenge_image").click(challenge_clicked);
    $(".review_box.active").click(review_box_clicked);
    $(".review_box.in_progress").click(review_box_clicked);
    $(".received_review").click(received_review_clicked);
}

function challenge_clicked(event) {
    var challenge = $(event.target).closest(".challenge");
    if (!challenge.hasClass("active")) {
        return;
    }
    var challenge_id = challenge.attr('id');
    var url = './get_challenge?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        window.history.pushState('', '', './challenge?id=' + challenge_id);
    });
}

function review_box_clicked(event) {
    var challenge_id = $(event.target).attr('challenge_id');
    var url = './get_challenge_review/?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        window.history.pushState('', '', './challenge_review?id=' + challenge_id);
    });
}

function received_review_clicked(event) {
    var challenge = $(event.target).parent();
    var challenge_id = challenge.attr('id');
    var url = './get_received_challenge_reviews/?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        window.history.pushState('', '', './received_challenge_reviews?id=' + challenge_id);
    });
}