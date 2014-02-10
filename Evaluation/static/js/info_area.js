$(function() {
    tinymce.init({
        // selector: "textarea#editor",
        mode : "exact",
        elements :"editor_stack_rev, editor_others",
        menubar: false,
        statusbar: false,
		toolbar: false,
	    plugins: "autoresize",
		autoresize_min_height: 100,
		autoresize_max_height: 800,
        readonly: 1
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