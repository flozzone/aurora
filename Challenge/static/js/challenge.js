$(stack_loaded);

function stack_loaded() {
    $(".stack").click(stack_clicked);
}

function stack_clicked(event) {
    var stack = $(event.target);
    var stack_id = stack.attr('id');
    var url = './stack?id=' + stack_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        $(challenge_loaded());
    });
}

function challenge_loaded() {
    $(".challenge").click(challenge_clicked);
}

function challenge_clicked(event) {
    var challenge = $(event.target);
    var challenge_id = challenge.attr('id');
    var url = './challenge?id=' + challenge_id;
    $.get(url, function (data) {
        $('#detail_area').html(data);
        initialize_textbox(challenge_id);
    });
}

function initialize_textbox(challenge_id) {
    tinymce.init({
        selector: "textarea#editor",
        plugins: "image",
        setup: function(editor) {
            editor.on('change', function(e) {
               elaboration_autosave(e, challenge_id);
            });
        }
    });

    $('.submit').click(submit_clicked);
}

function elaboration_autosave(e, challenge_id) {
    var elaboration_text = tinyMCE.activeEditor.getContent().toString();
    var data = {
        challenge_id: challenge_id,
        elaboration_text: elaboration_text
    };
    var args = { type:"POST", url:"./autosave/", data:data,
        error: function() {
            alert('error elaboration autosave');
        } };
    $.ajax(args);
}

function submit_clicked(event) {
    console.log(tinyMCE.activeEditor.getContent().toString());

    var challenge = $(event.target);
    var challenge_id = challenge.attr('id');

    var url = './submit?id=' + challenge_id;
    $.get(url, function (data) {
    });
}
