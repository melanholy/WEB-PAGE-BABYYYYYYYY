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

function setInfoCookie() {
    var ss = screen.width + 'x' + screen.height;
    var tz = new Date().getTimezoneOffset();
    document.cookie = 'ss='+ss+'; expires=0; path=/';
    document.cookie = 'tz='+tz+'; expires=0; path=/';
}

setInfoCookie();
