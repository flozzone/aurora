$( document ).ready(function() {
    setInterval(function(){
        $.get(UPDATE_SLIDES_URL + last_update + '/', {}, function(response){
            console.log("got a response:");
            console.log(response);
            last_update = response.last_update
        }, 'json');
    }, 4000);
});