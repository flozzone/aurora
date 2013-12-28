$(view_review_loaded);

function view_review_loaded() {
    $('.escalate_button').click(escalate_clicked);
}

function escalate_clicked(event) {
    console.log(event.target);
    var url = '/review/escalate?id=' + $(event.target).attr("id")
    $.get(url, function (data) {
        location.reload();
    });
}