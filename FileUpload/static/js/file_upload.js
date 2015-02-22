Dropzone.autoDiscover = false;

$(file_upload_loaded);

var dropzone_instance;

function file_upload_loaded() {
    if (!$(".file_upload").length) {
        return;
    }
    var is_submitted = $("#dropzone").hasClass('is_submitted');

    var read_write_options = {
        maxFilesize: 100, // MB
        addRemoveLinks: true,
        dictRemoveFile: 'REMOVE',
        acceptedFiles: $('.file_upload').attr('accepted_files'),
        init: function () {
            this.on("error", function (file, error, xhr) {
                console.log(error);
                $(file.previewElement).fadeOut(5000, function () {dropzone_instance.removeFile(file);});
            });
            this.on("success", function (file, response) {
                revert_submit_clicked();
                var data = JSON.parse(response);
                file.id = data.id;
                var elaboration_id = $('#elaboration_id').val();
                if (file.type === 'application/pdf') {
                    console.log('this is a pdf');
                    dropzone_instance.createThumbnailFromUrl(file, static_url + 'img/pdf_icon.jpg', function(dataURL) {$(file.previewElement).find('img').attr('src', dataURL)}, 'image/png');
                    $(file.previewElement).addClass('dz-image-preview');
                    $(file.previewElement).addClass('dz-complete');
                    $(file.previewElement).addClass('dz-success');
                    $(file.previewElement).find('img').show();
                } else {
                    var errors = 0;
                    dropzone_instance.files.forEach(function (check_file) {
                        if (check_file.status === "error") {
                            errors++;
                        }
                        if (file === check_file) {
                            $(file.previewElement).append('<div class="fig">Fig: ' + (dropzone_instance.files.indexOf(file) + 1 - errors) + '</div>');
                        }
                    });
                }
                $(file.previewElement).wrap(function () {
                    return "<a href='" + data.url + "' target='_blank' title='" + file.name + "'></div>";
                });
            });
            this.on("removedfile", function (file) {
                revert_submit_clicked();
                if (file.id) {
                    var url = '/fileupload/remove?id=' + file.id;

                    $.get(url, function (data) {});
                    if (file.type !== 'application/pdf') {
                        var i = 0;
                        dropzone_instance.files.forEach(function (file) {
                            if (file.status !== "error") {
                                i++;
                            }
                            $(file.previewElement).find('.fig').replaceWith('<div class="fig">Fig: ' + i + '</div>');
                        });
                    }
                }
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
    load_files(elaboration_id, is_submitted)
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
        var i = 0;
        data.forEach(function (file) {
            i++;
            // Create the mock file:
            var mockFile = { name: file.name, size: file.size, path: file.url, type: 'image/*', status: Dropzone.success};
            dropzone_instance.emit("addedfile", mockFile);
            if (file.url.match(/pdf$/)) {
                console.log('I am a pdf');
                dropzone_instance.createThumbnailFromUrl(mockFile, static_url + 'img/pdf_icon.jpg', function(dataURL) {$(file.previewElement).find('img').attr('src', dataURL)}, 'image/png');
                $(mockFile.previewElement).addClass('dz-image-preview');
            } else {
                dropzone_instance.createThumbnailFromUrl(mockFile, file.url, function(dataURL) {$(mockFile.previewElement).find('img').attr('src', dataURL)}, 'image/png');
                $(mockFile.previewElement).append('<div class="fig">Fig: ' + i + '</div>');
            }
            mockFile.id = file.id;
            $(mockFile.previewElement).find(".dz-progress").remove();
            $(mockFile.previewElement).wrap(function () {
                return "<a href='" + file.url + "' target='_blank' title='" + mockFile.name + "'></div>";
            });
            dropzone_instance.files.push(mockFile);
        });
    });
}