$(challenge_loaded);

function challenge_loaded() {
    $(".challenge").click(challenge_clicked);
}

function challenge_clicked(event) {
    var challenge = $(event.target);
    var challenge_id = challenge.attr('id');
    var url = './challenge?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        initialize_textbox();
    });
}

function initialize_textbox() {
    tinymce.init({
        selector: "textarea",
        plugins: "image"
    });

    $('#submit').click(submit_clicked);
}

function submit_clicked() {
    console.log(tinyMCE.activeEditor.getContent());
}