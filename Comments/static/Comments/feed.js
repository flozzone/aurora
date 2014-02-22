/**
 * Created by peterpur on 22.2.2014.
 */



$(window).load( function() {
		filter(getCookie('filtercookie'));
})


function filter(fx) {
	document.cookie = "filtercookie="+fx;
	if (typeof fx == "string") {fx = parseInt(fx);}
	switch(fx) {
	case 1: $('.response_top,.comment_top').next().show().next().show();$('.r_list').show(); break;
	case 2: $('.response:not(.staff_author)').children('.response_top').next().hide().next().hide();
			$('.comment:not(.staff_author)').children('.comment_body').hide().next().hide();
			$('#'+$('.response.staff_author').parent().attr('class').split(' ')[0].slice(2)).children('.comment_body').show().next().show(); break;
	case -1:$('.neg0').next().hide().next().hide(); break;
	case -5:$('.neg5').next().hide().next().hide(); break;
	case 0: $('.response_top,.comment_top').next().hide().next().hide();$('.r_list').hide(); break;
	}
}




function getCookie(cname)
{
var name = cname + "=";
var ca = document.cookie.split(';');
for(var i=0; i<ca.length; i++) 
  {
  var c = ca[i].trim();
  if (c.indexOf(name)==0) return c.substring(name.length,c.length);
  }
return "";
}
