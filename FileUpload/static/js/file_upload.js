$(file_upload_loaded);

function file_upload_loaded() {
    Dropzone.options.myAwesomeDropzone = {
        maxFilesize: 100, // MB
        init: function () {
            var _this = this;
            this.on("success", function (file, response) {
                setTimeout(
                    function () {
                        _this.removeAllFiles();
                    }, 1000);
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