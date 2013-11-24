$(stack_loaded);

function stack_loaded() {
    $(".challenge.active").click(challenge_clicked);
    $(".review.active").click(review_clicked);
}

function challenge_clicked(event) {
    var challenge = $(event.target).closest(".challenge");
    var challenge_id = challenge.attr('id');
    var url = './get_challenge?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        window.history.pushState('', '', './challenge?id=' + challenge_id);
    });
}

function review_clicked(event) {
    var challenge_id = $(event.target).attr('challenge_id');
    var url = './get_challenge_review?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        window.history.pushState('', '', './challenge_review?id=' + challenge_id);
    });
}
