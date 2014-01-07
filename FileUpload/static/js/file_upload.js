Dropzone.autoDiscover = false;

$(file_upload_loaded);
var dropzone_instance;
function file_upload_loaded() {
    var is_submitted = $("#dropzone").hasClass('is_submitted');

    var read_write_options = {
        maxFilesize: 100, // MB
        addRemoveLinks: true,
        init: function () {
            if (is_submitted) {
                console.log('is submitted');
                $('.dropzone').removeClass('dz-clickable');
                $('.dropzone').click(function (e) {
                    console.log('bla');
                    e.preventDefault();
                    return false;
                });
            }
            this.on("success", function (file, response) {
                file.image_url = response;
                var elaboration_id = $('#elaboration_id').val();
                $(file.previewElement).find('img').wrap(function () {
                    return "<a href='/" + file.image_url + "' data-lightbox='preview' title='" + file.name + "'></div>";
                });
                $(file.previewElement).find('img').attr('src', '/' + file.image_url);
            });
            this.on("removedfile", function (file) {
                var url = '/fileupload/remove?url=' + file.image_url;
                $.get(url, function (data) {
                });
            });
        }
    };

    var read_options = {
        clickable: false,
        init: function () {
            $('.dropzone').removeClass('dz-clickable');
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
            load_files(elaboration_id)
        });
    } else {
        load_files(elaboration_id)
    }
}

function load_files(elaboration_id) {
    var url = '/fileupload/all?elaboration_id=' + elaboration_id;
    $.get(url, function (data) {
        var data = JSON.parse(data);
        data.forEach(function (file) {
            // Create the mock file:
            var mockFile = { name: file.name, size: file.size, image_url: file.path, type: 'image.*', status: Dropzone.success};
            dropzone_instance.emit("addedfile", mockFile);
            dropzone_instance.emit("thumbnail", mockFile, '/' + file.path);
            dropzone_instance.files.push(mockFile);
            $(mockFile.previewElement).find('img').wrap(function () {
                return "<a href='/" + file.path + "' data-lightbox='preview' title='" + file.name + "'></div>";
            });
        });
    });
}