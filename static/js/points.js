$(window).load( function() {
    "use strict";
	loadTabs();
});

function loadTabs() {
	z = getCookie('pointC.final_list.'+$('#the_username').data('username'))
	if (z=='true') {$('.final_list').show(0);}
	z = getCookie('pointC.sub_list.'+$('#the_username').data('username'))
	if (z=='true') {$('.sub_list').show(0);}
	z = getCookie('pointC.work_list.'+$('#the_username').data('username'))
	if (z=='true') {$('.work_list').show(0);}
}


function tggle(area) {
	statu_s = $(area).is(':visible');
	if (statu_s) {$(area).slideUp(200)} else {$(area).slideDown(200)}	
	statu_s = !statu_s;
	var ckie = "pointC" + area + '.' + $('#the_username').data('username') + "=" + statu_s + "; expires=Tue, 18 Jan 2038";
	document.cookie = ckie;
	//var morgs = "clickcookie." + $('#the_username').data('username') + "=" + clickedComments.join(',') + "; expires=Tue, 18 Jan 2038 03:14:06 GMT";
	
	
}