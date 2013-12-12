$(review_loaded);

function review_loaded() {
    $('form').bind("keypress", function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            return false;
        }
    });
    $('.review_submit').click(submit_clicked);
}

function submit_clicked(event) {
    event.preventDefault();
    var challenge = $(".challenge").first();
    var challenge_id = challenge.attr('id');
    var review = $(".review").first();
    var review_id = review.attr('id');
    var data = {};
    data['challenge_id'] = challenge_id;
    data['review_id'] = review_id;
    data['answers'] = [];
    $(".answer").each(function (index) {
        var answer_object = $(this);
        var answer = null;
        if (answer_object.hasClass('boolean_answer')) {
            answer = answer_object.find('input').first().is(':checked');
        } else {
            answer = answer_object.find('input').first().val();
        }
        data['answers'].push({
            'question_id': answer_object.attr('question_id'),
            'answer': answer
        });
    });
    data['appraisal'] = $('input[name=appraisal]:checked').val();
    data['awesome'] = $('input[name=awesome]').is(':checked');
    ajax_setup()
    var args = {
        type: "POST",
        url: "/challenges/challenge_review/review_answer/",
        data: JSON.stringify(data),
        error: function (data) {
            alert('error submitting review');
        },
        success: review_submitted
    };
    $.ajax(args);
}

function review_submitted() {
    window.location.href = '../../challenges/stack?id=' + stack_id;
}

