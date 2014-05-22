/**
 * Created by peterpur on 22.2.2014.
 */

var loadMore_Timer;

$(function() {
	loadMore_Timer = setTimeout(function(){clickLoadMore()},1000);
})

function clickLoadMore() {
	el = $('.endless_more')[0]
	if ($(el).length) {
		if (isScrolledIntoView(el)) {
			el.click();
		}
		loadMore_Timer = setTimeout(function(){clickLoadMore()},1000);
	}
}

function isScrolledIntoView(el)
{
    var elemTop = el.getBoundingClientRect().top;
    var elemBottom = el.getBoundingClientRect().bottom;

    var isVisible = (elemTop >= 0) && (elemBottom <= window.innerHeight);
    return isVisible;
}



$(function() {
	$('.course_selected').addClass('irrelevant');
	$('#feed-li').addClass('uRhere');
	window.document.title="Aurora: Newsfeed"
	$('.feed_header').click(function(){
		$('#content_'+$(this).attr('id')).slideToggle('fast');
	})
});

var updateNew_Timer;

$(window).load( function() {
    "use strict";
	loadFilter();
});

function loadFilter() {
    "use strict";
	filter(getCookie('filtercookie.'+$('#the_username').data('username')));
	doClickFilter();
}

function doClickFilter () {
	"use strict";
	var ccCookieData = getCookie('clickcookie.'+$('#the_username').data('username'));
	if (ccCookieData != null) {
		var clickedComments = ccCookieData.split(',');
		for (var i=0;i<clickedComments.length;i++) {
			if (clickedComments[i] != "") {filterByClick('#comment_'+clickedComments[i])}
		}
	}
}

function filterClick(fx,usr) {
	document.cookie = "clickcookie." + $('#the_username').data('username') + "= " + "; expires=Tue, 18 Jan 2038 03:14:06 GMT";
	filter(fx,usr);
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
        case 1: // show all comments
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            break;
        case 2: // lecturers
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            $('.response:not(.staff_author):not(.author_author),.comment:not(.staff_author):not(.author_author)').addClass('hided');
            $('#' + $('.response.staff_author').parent().attr('class').split(' ')[0].slice(2)).removeClass('hided');
            break;
        case 3: // good comments 
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            $('.not3:not(.author_author)').addClass('hided');
            break;
		case 4:  // top-level comments, no replies
            $('.response,.comment,.r_list').removeClass('hided');
            $('.response').addClass('hided');
			break;
		case 99:  // only staff comments
        	$('.response,.comment,.r_list').removeClass('hided');
            $('.response:not(.staff_visibility),.comment:not(.staff_visibility)').addClass('hided');
            $('.response:not(.staff_visibility),.comment:not(.staff_visibility)').addClass('hided');
			break;
		case 98:  // no staff comments
        	$('.response,.comment,.r_list').removeClass('hided');
            $('.response.staff_visibility,.comment.staff_visibility').addClass('hided');
			break;
        case -5: // no lame comments
            $('.response,.comment,.r_list').removeClass('hided');
            $('.r_list').show();
            $('.neg5:not(.author_author)').addClass('hided');
            break;
        case 0: // new comments
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
	clearTimeout(loadMore_Timer);
	loadMore_Timer = setTimeout(function(){clickLoadMore()},1000);
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
	var ccCookieData = getCookie('clickcookie.'+$('#the_username').data('username'));
	if (ccCookieData != null && ccCookieData != "") {
		var clickedComments = ccCookieData.split(',');
	} 
	else {
		var clickedComments = new Array()
	}
//	$('.filterbtn').removeClass('hilited');
	var thisID = $(aDiv).data('comment_number');
	var indexID = $.inArray(thisID.toString(),clickedComments);
	if (indexID==-1) {clickedComments.push(thisID)} else {clickedComments.splice(indexID,1)}
	var morgs = "clickcookie." + $('#the_username').data('username') + "=" + clickedComments.join(',') + "; expires=Tue, 18 Jan 2038 03:14:06 GMT";;
//	alert (morgs);
	document.cookie = morgs;
	
	filterByClick(aDiv);	
}

function filterByClick(aDiv) {
    "use strict";
	$(aDiv).toggleClass('hided');
	if ($(aDiv).hasClass('comment')) {
		if ($(aDiv).hasClass('hided')) {
			$('.r_'+$(aDiv).attr('id')).addClass('hided');
		}
		else {
			$('.r_'+$(aDiv).attr('id')).removeClass('hided');
			$('.'+$(aDiv).attr('id')).removeClass('hided');
		}
	}	
}


function markT(usr) {
    "use strict";

	var s = Date.now() /1000 || 0;
	s = s-30;
	var a = "filterTimeCookie." + usr + "=" + s.toString() + "; expires=Tue, 18 Jan 2038 03:14:06 GMT";
	document.cookie = a;
}


function toTimestamp(strDate){
    "use strict";

	var dat = Date.parse(strDate);
	return dat/1000;
}
