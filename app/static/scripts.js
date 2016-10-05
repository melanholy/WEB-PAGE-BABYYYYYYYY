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
    var xhr = new XMLHttpRequest();

    var ss = screen.width + 'x' + screen.height;
    var body = 'ss=' + encodeURIComponent(ss) +
               '&csrf_token=' + encodeURIComponent(csrf) +
               '&path=' + encodeURIComponent(window.location.pathname) +
               '&ua=' + encodeURIComponent(navigator.userAgent);

    xhr.open('POST', '/visit', true);
    xhr.setRequestHeader(
        'Content-Type',
        'application/x-www-form-urlencoded'
    );

    xhr.send(body);
}
