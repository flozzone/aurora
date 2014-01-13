Dropzone.autoDiscover = false;

$(file_upload_loaded);
var dropzone_instance;
function file_upload_loaded() {
    if (! $(".file_upload").length ) {
        return;
    }
    var is_submitted = $("#dropzone").hasClass('is_submitted');

    var read_write_options = {
        maxFilesize: 100, // MB
        addRemoveLinks: true,
        acceptedFiles: $('.file_upload').attr('accepted_files'),
        init: function () {
            this.on("success", function (file, response) {
                file.path = response;
                var elaboration_id = $('#elaboration_id').val();
                if (file.type === 'application/pdf') {
                    $(file.previewElement).addClass('dz-image-preview');
                    $(file.previewElement).find('img').show();
                    $(file.previewElement).find('img').attr('src', '/static/img/pdf_icon.jpg');
                    $(file.previewElement).find('img').attr('alt', file.path);
                    $(file.previewElement).find('img').wrap(function () {
                        return "<a href='/" + file.path + "' title='" + file.name + "'></div>";
                    });
                } else {
                    $(file.previewElement).find('img').wrap(function () {
                        return "<a href='/" + file.path + "' data-lightbox='preview' title='" + file.name + "'></div>";
                    });
                    $(file.previewElement).find('img').attr('src', '/' + file.path);
                }
            });
            this.on("removedfile", function (file) {
                var url = '/fileupload/remove?url=' + file.path;
                $.get(url, function (data) {
                });
            });
        }
    };

    var read_options = {
        clickable: false,
        init: function () {
            $('.dropzone').removeClass('dz-clickable');
            $('.dz-message').remove();
        }
    };
    if (is_submitted) {
        Dropzone.options.dropzone = read_options;
    } else {
        Dropzone.options.dropzone = read_write_options;
    }
    dropzone_instance = new Dropzone("#dropzone");
    var elaboration_id = $('#elaboration_id').val();
    if (elaboration_id === '') {
        var challenge_id = $('.challenge').attr('id');
        var url = '/elaboration/create?id=' + challenge_id;
        $.get(url, function (data) {
            elaboration_id = data;
            $('#elaboration_id').val(elaboration_id);
            load_files(elaboration_id, is_submitted)
        });
    } else {
        load_files(elaboration_id, is_submitted)
    }
}

function load_files(elaboration_id, is_submitted) {
    var url = '/fileupload/all?elaboration_id=' + elaboration_id;
    $.get(url, function (data) {
        var data = JSON.parse(data);
        if (data.length === 0 && is_submitted) {
            $('.file_upload').hide();
            return;
        }
        $('.file_upload').show();
        data.forEach(function (file) {
            // Create the mock file:
            var mockFile = { name: file.name, size: file.size, path: file.path, type: 'image/*', status: Dropzone.success};
            dropzone_instance.emit("addedfile", mockFile);

            if (file.path.match(/pdf$/)) {
                dropzone_instance.emit("thumbnail", mockFile, '/static/img/pdf_icon.jpg');
                $(mockFile.previewElement).find('img').wrap(function () {
                    return "<a href='/" + file.path + "' title='" + file.name + "'></div>";
                });
            } else {
                dropzone_instance.emit("thumbnail", mockFile, '/' + file.path);
                $(mockFile.previewElement).find('img').wrap(function () {
                    return "<a href='/" + file.path + "' data-lightbox='preview' title='" + file.name + "'></div>";
                });
            }
            dropzone_instance.files.push(mockFile);
        });
    });
}