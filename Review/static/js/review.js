$(review_loaded);

function review_loaded() {
    $('.submit').click(submit_clicked);
}

function submit_clicked(event) {
    console.log("test");
}