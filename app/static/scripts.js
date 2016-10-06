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
