$(elaboration_files_loaded);

function elaboration_files_loaded() {

    $(".upload_preview").each(function (i, preview) {
        var details = $(preview).find(".upload_details a");
        var img = $(details).find("img");
        convertImgToBase64URL($(details).attr('href'), function (dataURL) {$(img).attr('src', dataURL)}, 'image/png');
    });
}

function convertImgToBase64URL(url, callback, outputFormat){
    var canvas = document.createElement('CANVAS'),
        ctx = canvas.getContext('2d'),
        img = new Image;
    img.crossOrigin = 'Anonymous';
    img.onload = function(){
        var dataURL;
        canvas.height = img.height;
        canvas.width = img.width;
        ctx.drawImage(img, 0, 0);
        dataURL = canvas.toDataURL(outputFormat);
        callback(dataURL);
        canvas = null;
    };
    img.src = url;
}