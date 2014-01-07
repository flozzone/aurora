Dropzone.autoDiscover = false;

$(file_upload_loaded);

function file_upload_loaded() {
    Dropzone.options.dropzone = {
        maxFilesize: 100, // MB
        addRemoveLinks: true,
        init: function () {
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
                $.get(url, function (data) {});
            });
        }
    };
    var dropzone = new Dropzone("#dropzone");
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
            dropzone.emit("addedfile", mockFile);
            dropzone.emit("thumbnail", mockFile, '/' + file.path);
            dropzone.files.push(mockFile);
            $(mockFile.previewElement).find('img').wrap(function () {
                return "<a href='/" + file.path + "' data-lightbox='preview' title='" + file.name + "'></div>";
            });
        });
    });
}