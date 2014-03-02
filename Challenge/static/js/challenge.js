$(challenge_loaded);

function challenge_loaded() {
    var challenge_id = $('.challenge').attr('id');
    tinymce.init({
        selector: "textarea#editor",
        paste_retain_style_properties: "font-size,bold,italic",
        paste_text_linebreaktype: "p",
        valid_elements: "p,strong,em,span,ul,ol,li,sub,br,sup,table,tbody,tr,td,div",
        paste_preprocess: function (plugins, args) { // remove all links
            var content;
            try {
                content = $(args.content);
                if (content.selector === "") {
                content.find('a').replaceWith(function () {
                    return $(this).text()
                });
                var fullHtml = "";
                $(content).each(function () {
                    fullHtml += '<p>' + $(this).html() + '</p>';
                });
                args.content = fullHtml;
            }
            } catch (error) {
                // in case the content is not a valid markup
            }
        },
        menubar: false,
        theme: 'modern',
        statusbar: false,
        fontsize_formats: "0.8em 1em 1.2em 1.6em 2em",
        toolbar1: "undo redo | bold italic | fontsizeselect | alignleft aligncenter | bullist numlist indent outdent | subscript superscript | table",
        plugins: "autoresize table paste",
        autoresize_min_height: 200,
        autoresize_max_height: 800,
        setup: function (editor) {
            editor.on('change', function (e) {
                elaboration_autosave(e, challenge_id);
            });
        }
    });

    tinymce.init({
        // selector: "textarea#editor",
        mode: "exact",
        elements: "editor_challenge",
        menubar: false,
        statusbar: false,
        toolbar: false,
        plugins: "autoresize",
        autoresize_min_height: 100,
        autoresize_max_height: 800,
        readonly: 1,
        oninit: function () {
            var height = $('#editor_challenge_ifr').height() + 50;
            $('#editor_challenge_ifr').height(height);
        }
    });

    $('.submit').click(submit_clicked);
    $('.real_submit').click(real_submit_clicked);
}

function elaboration_autosave(e, challenge_id) {
    revert_submit_clicked();
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
    window.scrollBy(0, 200);
}

function revert_submit_clicked() {
    $('.submit').show();
    $('.submission_text').hide();
}

function real_submit_clicked(event) {
    var challenge = $('.challenge');
    var challenge_id = challenge.attr('id');
    var stack_id = challenge.attr('stack');
    var url = './submit?id=' + challenge_id;
    $.get(url, function (data) {
        window.location.href = "/challenges/stack?id=" + stack_id;
    });
}