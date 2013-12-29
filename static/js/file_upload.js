$(file_upload_loaded);

function file_upload_loaded() {
    Dropzone.options.myAwesomeDropzone = {
        maxFilesize: 100, // MB
        thumbnailWidth: 50,
        thumbnailHeight: 50,
        init: function () {
            var _this = this;
            this.on("success", function (file, response) {
                _this.removeAllFiles();
            });
            this.on("thumbnail", function (file, dataUrl) {
                $('.upload_history').append("<img src=" + dataUrl + " />");
            });
        }
    };
    $('#upload_button').click(file_upload_clicked);
}

function file_upload_clicked(event) {
    $('.file_upload_menu').toggle();
}