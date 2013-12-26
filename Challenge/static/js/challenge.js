$(challenge_loaded);

function challenge_loaded() {
    var challenge_id = $('.challenge').attr('id');
    tinymce.init({
        selector: "textarea#editor",
        plugins: "image",
        setup: function (editor) {
            editor.on('change', function (e) {
                elaboration_autosave(e, challenge_id);
            });
        }
    });
    $('.submit').click(submit_clicked);
    $('.real_submit').click(real_submit_clicked);
}

function elaboration_autosave(e, challenge_id) {
    var elaboration_text = tinyMCE.activeEditor.getContent().toString();
    var data = {
        challenge_id: challenge_id,
        elaboration_text: elaboration_text
    };
    var args = { type: "POST", url: "./autosave/", data: data,
        error: function () {
            alert('error elaboration autosave');
        } };
    $.ajax(args);
}

function submit_clicked(event) {
    $('.submit').hide();
    $('.submission_text').show();
}
function real_submit_clicked(event) {
    var challenge = $(event.target);
    var challenge_id = challenge.attr('id');
    var url = './submit?id=' + challenge_id;
    $.get(url, function (data) {
        window.location.href = "./";
    });
}