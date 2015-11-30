$(document).ready(function(){
    $(".tag_input").autocomplete();
});

$(function() {
   $(".tag_input").click(function(event) {
       event.stopPropagation();
       $(".tag_input").autocomplete( "search", "" );
   });
});

$(function() {
   $(".add_tags_btn").click(function(event) {
       event.stopPropagation();
       var tag_input = $(this).prev();
       var text = tag_input.text();
       var object_id = tag_input.attr('object_id');
       var content_type_id = tag_input.attr('content_type_id');
       var tags = $(".tags.tags-" + content_type_id + '-' + object_id);
       var data = {
                text: text,
                object_id: object_id,
                content_type_id: content_type_id
            };

       var args = { type: "POST", url: "./add_tags/", data: data,
           success: function (data) {
               tags.html(data);
               tag_input.text("");
           }
       };
       $.ajax(args);
   });
});

$(function() {
   $(".tag").click(function(event) {
       event.stopPropagation();
   });
});

$(function() {
   $(".tag_remove").click(function(event) {
       event.stopPropagation();
       var tag = $(this).attr('name');
       var object_id = $(this).attr('object_id');
       var content_type_id = $(this).attr('content_type_id');
       var tags = $(".tags.tags-" + content_type_id + '-' + object_id);
       var data = {
                tag: tag,
                object_id: object_id,
                content_type_id: content_type_id
            };
       var args = { type: "POST", url: "./remove_tag/", data: data,
           success: function (data) {
               tags.html(data);
           }
       };
       $.ajax(args);
   });
});

$(function() {
    $(".tag_input").autocomplete({
        //source: "./autocomplete_tag/",
        source: function(request, response) {
          $.get('./autocomplete_tag/', { term: request.term, content_type_id: this.element.attr('content_type_id') }, function(data) {
            response(data);
          });
         },
        select: function (event, ui) {
            var tag_input = $(this);
            var text = ui.item.value     // select value from autocomplete box
            var object_id = $(this).attr('object_id');
            var content_type_id = $(this).attr('content_type_id');
            var tags = $(".tags." + object_id);
            var data = {
                text: text,
                object_id: object_id,
                content_type_id: content_type_id
            };
            var args = { type: "POST", url: "./add_tags/", data: data,
                success: function (data) {
                    tags.html(data);
                    tag_input.text("");
                }
            };
            $.ajax(args);
        },
        minLength: 2
    });
});
