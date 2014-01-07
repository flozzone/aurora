Dropzone.autoDiscover = false;

$(file_upload_loaded);

function file_upload_loaded() {
    Dropzone.options.dropzone = {
        maxFilesize: 100, // MB
        addRemoveLinks: true,
        init: function () {
            this.on("success", function (file, response) {
                file.image_url = response;
                var elaboration_id = $('.file_upload').attr('id');
                $(file.previewElement).find('img').wrap(function () {
                    return "<a href='/" + file.image_url + "' data-lightbox='preview' title='" + file.name + "'></div>";
                });
                $(file.previewElement).find('img').attr('src', '/' + file.image_url);
            });
            this.on("removedfile", function (file) {
                console.log(file);
                var url = '/fileupload/remove?url=' + file.image_url;
                $.get(url, function (data) {
                });
            });
        }
    };
    var dropzone = new Dropzone("#dropzone");
    var elaboration_id = $('.file_upload').attr('id');
    var url = '/fileupload/all?elaboration_id=' + elaboration_id;
    $.get(url, function (data) {
        var data = JSON.parse(data);

        data.forEach(function (file) {
            console.log(file);
            // Create the mock file:
            var mockFile = { name: file.name, size: file.size, image_url: file.path, type: 'image.*'};
            dropzone.emit("addedfile", mockFile);
            dropzone.emit("thumbnail", mockFile, '/' + file.path);
            $(mockFile.previewElement).find('img').wrap(function () {
                return "<a href='/" + file.path + "' data-lightbox='preview' title='" + file.name + "'></div>";
            });
            // If you use the maxFiles option, make sure you adjust it to the
            // correct amount:
            // var existingFileCount = 0; // The number of files already uploaded
            //dropzone.options.maxFiles = dropzone.options.maxFiles - existingFileCount;
        });
    });
}