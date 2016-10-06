console.log('YOU WANT A DWARF?\r\n\
\r\n\
######################\r\n\
######################\r\n\
#####            #####\r\n\
###    ########    ###\r\n\
###  ############  ###\r\n\
###  ##  ####  ##  ###\r\n\
###  ############  ###\r\n\
###  ##        ##  ###\r\n\
###  ####    ####  ###\r\n\
###    ########    ###\r\n\
#####            #####\r\n\
######################\r\n\
######################\r\n\
\r\n\
THERE\'S YOUR DAMN DWARF.')

function registerVisit(csrf) {
    var ss = screen.width + 'x' + screen.height;
    var data = {
      'ss': ss, 'csrf_token': csrf,
      'path': window.location.pathname,
      'ua': navigator.userAgent
    }
    ajaxSend('/visit', 'POST', data, null);
}

function getStats() {
	var tz = new Date().getTimezoneOffset();
	var path = window.location.pathname;

	var stats = document.getElementById('stats');
	stats.setAttribute('src', '/stats?tz=' + tz + '&path=' + path)
}
