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

function addStatsToPage() {
    var statsDiv = document.getElementById('stats');

    var statsImg = document.createElement('img');
    statsImg.width = '270';
    statsImg.height = '34';
    statsImg.alt = 'Статистика посещений';

    var tz = new Date().getTimezoneOffset();
    var path = window.location.pathname;

    statsImg.setAttribute('src', '/stats?tz=' + tz + '&path=' + path);

    statsDiv.appendChild(statsImg);
}
