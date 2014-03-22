
$(function(){
	$('.challenge-text').ellipsis({
	    row: 4,
		char: '… (click for full text)',
	    onlyFullWords: true,
	});	
	$('.course_selected').removeClass('irrelevant');
	$('#challenges-li').addClass('uRhere');
	window.document.title="Aurora: Challenges"
});




$(stack_loaded);



function stack_loaded() {
	$(".one_challenge").click(challenge_clicked);
	$(".go_challenge").click(challenge_clicked)
    $(".review_box.active").click(review_box_clicked);
    $(".review_box.in_progress").click(review_box_clicked);
    $(".received_review").click(received_review_clicked);
}

function challenge_clicked(event) {
    var challenge = $(event.target);
    if (!challenge.hasClass("active")) {
        return;
    }
    var challenge_id = challenge.attr('challenge_id');
    window.location.href = './challenge?id=' + challenge_id
}

function review_box_clicked(event) {
    var challenge_id = $(event.target).parent().attr('challenge_id');
    window.location.href = './challenge_review?id=' + challenge_id;
}

function received_review_clicked(event) {
    var challenge = $(event.target).parent().parent();
    var challenge_id = challenge.attr('challenge_id');
    window.location.href = './challenge?id=' + challenge_id
}

