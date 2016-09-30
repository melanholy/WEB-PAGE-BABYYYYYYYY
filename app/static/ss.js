function send_ss(csrf) {
    var xhr = new XMLHttpRequest();

    var ss = screen.width + 'x' + screen.height;
    var body = 'ss=' + encodeURIComponent(ss) +
               '&csrf_token=' + encodeURIComponent(csrf) +
               '&path=' + encodeURIComponent(window.location.pathname) +
               '&ua=' + encodeURIComponent(navigator.userAgent);

    xhr.open('POST', '/ss', true);
    xhr.setRequestHeader(
        'Content-Type',
        'application/x-www-form-urlencoded'
    );

    xhr.send(body);
}