$(function() {
	$('#challenges-li').addClass('uRhere');
	window.document.title="Aurora: Challenges";
	$('textarea').keyup(function() {
	    $(this).height( 0 );
	    $(this).height( this.scrollHeight );
	});
	$('textarea').each(function() {
	    $(this).height( 0 );
	    $(this).height( this.scrollHeight );
	});
});


$(review_loaded);

function review_loaded() {
    tinymce.init({
        mode : "exact",
        elements :"editor_review",
        menubar: false,
        statusbar: true,
		toolbar: false,
		height: 300,
        readonly: 1,
        plugins: "wordcount"
    });

//    $('form').bind("keypress", function (e) {
//        if (e.keyCode == 13) {
//            e.preventDefault();
//            return false;
//        }
//    });
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
    var missing_answer = false;
    $(".question_container").each(function (index) {
        var answer_object = $(this).find('.answer');
        var answer = null;
        if (answer_object.hasClass('boolean_answer')) {
            answer = answer_object.find('input:checked')
            if (answer.length === 0) {
                missing_answer = true;
            }
            answer = answer.val();
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

    var appraisal = $('input[name=appraisal]:checked');
    if (appraisal.length === 0) {
        missing_answer = true
    }

    if (missing_answer) {
        alert("please fill out all answers");
        return;
    }
    data['appraisal'] = appraisal.val();
    ajax_setup()
    var args = {
        type: "POST",
        url: REVIEW_ANSWER_URL,
        data: JSON.stringify(data),
        error: function (data) {
            alert('error submitting review');
        },
        success: review_submitted
    };
    $.ajax(args);
}

function review_submitted() {
    window.location.href = STACK_URL + '?id=' + stack_id;
}

