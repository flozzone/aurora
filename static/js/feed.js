/**
 * Created by peterpur on 22.2.2014.
 */

$(function() {
	$('.course_selected').addClass('irrelevant');
	$('#feed-li').addClass('uRhere');
});

var updateNew_Timer;

$(window).load( function() {
    "use strict";

	loadFilter();
});

function loadFilter() {
    "use strict";

	filter(getCookie('filtercookie.'+$('#the_username').data('username')));
}

function filter(fx,usr) {
    "use strict";

    if (typeof usr !== 'undefined') {
        document.cookie = "filtercookie." + usr + "=" + fx + "; expires=Tue, 18 Jan 2038 03:14:06 GMT";
    }

    if (typeof fx === "string") {
        fx = parseInt(fx);
    }

	$('.filterbtn').removeClass('hilited');
	$('#'+fx).addClass('hilited');
	$('#new_date').text(''); clearTimeout(updateNew_Timer);

    switch (fx) {
        case 1:
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            break;
        case 2:
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            $('.response:not(.staff_author):not(.author_author),.comment:not(.staff_author):not(.author_author)').addClass('hided');
            $('#' + $('.response.staff_author').parent().attr('class').split(' ')[0].slice(2)).removeClass('hided');
            break;
		case 4:
            $('.response,.comment,.r_list').removeClass('hided');
            $('.response').addClass('hided');
			break;
        case -1:
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            $('.neg0:not(.author_author)').addClass('hided');
            break;
        case -5:
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            $('.neg5:not(.author_author)').addClass('hided');
            break;
        case 0:
            $('.response,.comment,.r_list').addClass('hided');
            $('.r_list').addClass('hided');
			var cookieName = 'filterTimeCookie.'+$('#the_username').data('username');
			var x = getCookie(cookieName);
			$('.comment').each(function(i){
				var c = $(this).data('date');
				if (c > x) {
					$(this).removeClass('hided');
				}
			});
			$('.response').each(function(i){
				var c = $(this).data('date');
				if (c > x) {
					$('#'+$(this).data('comment')).removeClass('hided');
					$('.r_'+$(this).data('comment')).removeClass('hided');
					$(this).removeClass('hided');
				}
			});
			updateNew();
            break;
    }
}

function updateNew() {
	var cookieName = 'filterTimeCookie.'+$('#the_username').data('username');
	var x = getCookie(cookieName);
	var y = Math.round(Date.now()/60000 - x/60);
	if (y<2) {y = ''}
	else if (y<60) {y = '(' + y + ' mins)'}
	else if (y<1440) {y = '(' + Math.round(y/60) + ' hours)'}
	else {y = '(' + Math.round(y/1440) + ' days)'}
	$('#new_date').text(y);
	updateNew_Timer = setTimeout(function(){updateNew()},60000);
}

function headClick(aDiv) {
    "use strict";

	$('.filterbtn').removeClass('hilited');
	$(aDiv).toggleClass('hided');
	if ($(aDiv).hasClass('comment')) {
		if ($(aDiv).hasClass('hided')) {
			$('.r_'+$(aDiv).attr('id')).addClass('hided');
		}
		else {
			$('.r_'+$(aDiv).attr('id')).removeClass('hided');
		}
	}
}


function markT(usr) {
    "use strict";

	var s = Date.now() /1000 || 0;
	var a = "filterTimeCookie." + usr + "=" + s.toString() + "; expires=Tue, 18 Jan 2038 03:14:06 GMT";
	document.cookie = a;
}


function toTimestamp(strDate){
    "use strict";

	var dat = Date.parse(strDate);
	return dat/1000;
}
