$(function () {
    $('.review_evaluation').click(review_evaluation_clicked);
});

function review_evaluation_clicked(event) {
    var target = $(event.target);
    var parent = target.parent();
    var children = parent.children();
    children.each(function () {
        var child = $(this);
        child.removeClass('active');
        child.removeClass('waiting');
    });
    var review_id = target.attr('review_id');
    var appraisal = target.attr('appraisal');
    target.addClass('waiting');
    send_review_evaluation(review_id, appraisal, target);
}

function send_review_evaluation(review_id, appraisal, target) {
    // REVIEW_EVALUATION_URL is declared in template challenge.html in Challenge
    $.get(REVIEW_EVALUATION_URL + '?appraisal=' + appraisal + '&review_id=' + review_id, function (data) {
        target.removeClass('waiting');
        target.addClass('active');
    });
}