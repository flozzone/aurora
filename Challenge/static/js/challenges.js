$(challenges_loaded);

function challenges_loaded() {
    $(".stack_imgs").click(stack_clicked);
}

function stack_clicked(event) {
    var stack = $(event.target).closest(".stack");
    var stack_id = stack.attr('id');
    window.location.href = './stack?id=' + stack_id;
}