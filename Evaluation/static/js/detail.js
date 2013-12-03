$(function() {
    $(".paginator_others").click(function(event) {
        var url = '/others?page=' + $(event.target).attr('id');
        $.get(url, function (data) {
            $('#info_area').html(data);
        });
    });
});