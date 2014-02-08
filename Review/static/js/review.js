$(review_loaded);

function review_loaded() {
    $('form').bind("keypress", function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            return false;
        }
    });
    $('#submit_button').click(submit_clicked);
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
    $(".question_container").each(function (index) {
        var answer_object = $(this).find('.answer');
        var answer = null;
        if (answer_object.hasClass('boolean_answer')) {
            answer = answer_object.find('input').first().is(':checked');
        } else {
            answer = answer_object.find('#text_answer').val();
        }
        var question = answer_object.parent().find('.question').first();
        var question_id = question.attr('id');
        if (question_id) {
            data['answers'].push({
                'question_id': answer_object.parent().find('.question').first().attr('id'),
                'answer': answer
            });
        }
    });
    data['appraisal'] = $('input[name=appraisal]:checked').val();

    ajax_setup()
    console.log(data);
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

