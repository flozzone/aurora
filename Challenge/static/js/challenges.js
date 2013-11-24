$(challenges_loaded);

function challenges_loaded() {
    $(".stack").click(stack_clicked);
}

function stack_clicked(event) {
    var stack = $(event.target).closest(".stack");
    var stack_id = stack.attr('id');
    var url = './get_stack?id=' + stack_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        window.history.pushState('', '', './stack?id=' + stack_id);
    });
}