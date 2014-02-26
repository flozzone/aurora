/**
 * Created by peterpur on 22.2.2014.
 */



$(window).load( function() {
	loadFilter();
})

function loadFilter() {
	filter(getCookie('filtercookie'));
}


function filter(fx) {
	document.cookie = "filtercookie="+fx+"; expires=Tue, 18 Jan 2038 03:14:06 GMT";
	if (typeof fx == "string") {fx = parseInt(fx);}
	$('.filterbtn').removeClass('hilited')
	$('#'+fx).addClass('hilited')
	switch(fx) {
	case 1: $('.response,.comment,.r_list').removeClass('hided');$('.r_list').show(); break;
	case 2: $('.response,.comment,.r_list').removeClass('hided');$('.r_list').show(); 
		 	$('.response:not(.staff_author):not(.author_author),.comment:not(.staff_author):not(.author_author)').addClass('hided');
			$('#'+$('.response.staff_author').parent().attr('class').split(' ')[0].slice(2)).removeClass('hided'); break;
	case -1:$('.response,.comment,.r_list').removeClass('hided');$('.r_list').show();
			$('.neg0:not(.author_author)').addClass('hided'); break;
	case -5:$('.response,.comment,.r_list').removeClass('hided');$('.r_list').show();
			$('.neg5:not(.author_author)').addClass('hided'); break;
	case 0: $('.response,.comment,.r_list').addClass('hided');$('.r_list').addClass('hided'); break;
	}
}

function getCookie(cname) {
var name = cname + "=";
var ca = document.cookie.split(';');
for(var i=0; i<ca.length; i++) 
  {
  var c = ca[i].trim();
  if (c.indexOf(name)==0) return c.substring(name.length,c.length);
  }
return "";
}


function headClick(aDiv) {
	$('.filterbtn').removeClass('hilited');
	$(aDiv).toggleClass('hided');
	if ($(aDiv).hasClass('comment')) {
		if ($(aDiv).hasClass('hided')) {
			$('.r_'+$(aDiv).attr('id')).addClass('hided')
		}
		else {
			$('.r_'+$(aDiv).attr('id')).removeClass('hided')
		}
	}
}
