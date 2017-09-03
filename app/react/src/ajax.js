function ajaxSend(path, type, args, callback) {
    var xhr = new XMLHttpRequest();
    if (type == 'POST') {
        var body = '';
        for (var key in args)
            body += key + '=' + encodeURIComponent(args[key]) + '&';
    }

    xhr.open(type, path, true);

    if (callback)
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200)
                callback(xhr);
        }

    if (type == 'POST')
    {
        xhr.setRequestHeader(
            'Content-Type',
            'application/x-www-form-urlencoded'
        );
        xhr.send(body);
    }
    else if (type == 'GET')
        xhr.send();
}
