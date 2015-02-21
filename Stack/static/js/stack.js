
$(function(){
	$('.challenge-text').ellipsis({
	    row: 4,
		char: '… (click for full text)',
	    onlyFullWords: true
	});	
	$('.course_selected').removeClass('irrelevant');
	$('#challenges-li').addClass('uRhere');
	window.document.title="Aurora: Challenges"
});




$(stack_loaded);



function stack_loaded() {
	$(".one_challenge").click(challenge_clicked);
    $(".review_box.active").click(review_box_clicked);
    $(".review_box.in_progress").click(review_box_clicked);
    $(".received_review").click(received_review_clicked);
}

function challenge_clicked(event) {
    event.stopPropagation();
    var challenge = $(event.target).closest(".one_challenge");
    var challenge_id = challenge.attr('challenge_id');
    window.location.href = './challenge?id=' + challenge_id
}

function review_box_clicked(event) {
    event.stopPropagation();
    var challenge_id = $(event.target).parent().attr('challenge_id');
    window.location.href = REVIEW_URL + '?id=' + challenge_id;
}

function received_review_clicked(event) {
    event.stopPropagation();
    var challenge = $(event.target).parent().parent();
    var challenge_id = challenge.attr('challenge_id');
    window.location.href = './challenge?id=' + challenge_id
}

