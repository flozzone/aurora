$(function() {
 $('.tag_input').keydown(function(e) {
	 keyP = e.which;
     if(keyP == 188 || keyP == 13 || keyP == 186) {
		$('.add_tags_btn').trigger( "click" );
		setInterval(function() {$('#tag_input').focus();},250);
		return false;
      }
  });
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
       var user_id = tag_input.attr('user_id');
       var tags = $(".tags." + user_id);
       var data = {
                text: text,
                user_id: user_id
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
       var user_id = $(this).attr('user_id');
       var tags = $(".tags." + user_id);
       var data = {
                tag: tag,
                user_id: user_id
            };
       var args = { type: "POST", url: "./remove_tag/", data: data,
           success: function (data) {
               console.log(tags);
               console.log(data);
               tags.html(data);
           }
       };
       $.ajax(args);
   });
});

$(function() {
    $("#tag_input").autocomplete({
        source: "./autocomplete_tag/",
        select: function (event, ui) {
            var tag_input = $(this);
            var text = ui.item.value     // select value from autocomplete box
            var user_id = $(this).attr('user_id');
            var tags = $(".tags." + user_id);
            var data = {
                text: text,
                user_id: user_id
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