import React from 'react';
import ReactDOM from 'react-dom';
import Base from './base/base.jsx';
import Router from './router.jsx';

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
THERE\'S YOUR DAMN DWARF.');

(function setInfoCookie() {
    var ss = screen.width + 'x' + screen.height;
    var tz = new Date().getTimezoneOffset();
    document.cookie = 'ss='+ss+'; expires=0; path=/';
    document.cookie = 'tz='+tz+'; expires=0; path=/';
})();

ReactDOM.render(
  <Base body={<Router />} />,
  document.getElementById('root')
);
