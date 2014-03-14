$(function() {
	$('.course_selected').removeClass('irrelevant');
	$('#challenges-li').addClass('uRhere');
	window.document.title="Aurora: Challenges"
});


$(challenges_loaded);

function challenges_loaded() {
    $(".stack").click(stack_clicked);
}

function stack_clicked(event) {
    var stack = $(event.target).closest(".stack");
    var stack_id = stack.attr('id');
    window.location.href = './stack?id=' + stack_id;
}