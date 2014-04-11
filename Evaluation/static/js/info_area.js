$(function() {
    tinymce.init({
        // selector: "textarea#editor",
        mode : "exact",
        elements :"editor_stack_rev, editor_others",
        menubar: false,
        statusbar: true,
		toolbar: false,
		height:300,
        readonly: 1,
        plugins: "wordcount",
    });
});

$(function() {
    $(".paginator_others").click(function(event) {
        var url = '/others?page=' + $(event.target).attr('id');
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
    });
});

$(function () {
    $(".review_answer").each(function () {
        this.style.height = (this.scrollHeight+5)+'px';
    });
});
