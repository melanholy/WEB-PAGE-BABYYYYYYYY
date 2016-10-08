if (!window.history.pushState) {
    window.history.pushState = function(one, two, url) {
        window.location.pathname = url;
    }
}
if (!document.getElementsByClassName) {
    document.getElementsByClassName = function(name) {
        return document.querySelectorAll('.' + name);
    }
}

function addCommentsToDocument(xhr) {
    var data = JSON.parse(xhr.responseText);
    var comment_section = document.getElementById('comments');
    comment_section.innerHTML = '';
    var list = document.createElement('ul');
    list.className = 'dollar-ul';
    comment_section.appendChild(list);
    for (var i = 0; i < data.length; i++) {
        var comment = document.createElement('li');
        comment.innerHTML = '[' + data[i]['author'] + ']<br>';
        comment.innerHTML += data[i]['text'] + '<br>';
        comment.innerHTML += '<span class="date">' + data[i]['date'] + '</span>';
        comment.innerHTML += '<hr>';
        list.appendChild(comment);
    }
}

function getComments(filename) {
    var path = '/comments?filename=' + encodeURIComponent(filename);
    ajaxSend(path, 'GET', [], addCommentsToDocument);
}

function sendComment() {
    var textarea = document.getElementsByName('text')[0];
    if (!textarea.value) {
        return;
    }

    var text = textarea.value;
    var id = document.getElementsByName('id_')[0].getAttribute('value');
    var csrf = document.getElementsByName('csrf_token')[0].getAttribute('value');
    var data = {'id_': id, 'csrf_token': csrf, 'text': text};

    textarea.value = '';

    ajaxSend(
        '/comment', 'POST', data,
        function(xhr) {
            if (xhr.responseText != 'ok')
                document.write(xhr.responseText);
            else
                getComments(id);
        }
    );
}

function expandImage(id) {
    window.history.pushState({}, "", '/' + 'gallery/' + id);

    toggleBigImage();
}

function setAsBackground() {
    href = document.getElementById('image-big').getAttribute('src');
    document.body.style.backgroundImage = 'url("' + href + '")';
    document.cookie = "back="+href+"; expires=0; path=/";
}

function hideModals() {
    var hids = document.getElementsByClassName('hid');
    for (var i = 0; i < hids.length; i++)
        hids[i].style.display = 'none';
    document.getElementById('help').style.display = 'none';

    window.history.pushState({}, "", '/gallery');
}

function showHelp() {
    var help = document.getElementById('help');
    var cross = document.getElementById('cross');
    var shade = document.getElementById('shade');
    cross.style.display = 'block';
    shade.style.display = 'block';
    help.style.display = 'block';
}

document.onkeydown = function(event) {
    var el = document.getElementById('image-big-div');
    if (el.style.display != 'none') {
        var el = document.getElementById('image-big');
        var next = parseInt(el.getAttribute('data-id'));
        if (event.keyCode == 39)
            next++;
        else if (event.keyCode == 37)
            next--;
        else if (event.keyCode == 27) {
            hideModals();
            return;
        }
        else
            return;

        pics_len = document.getElementsByClassName('gal-img').length;
        if (next < 0)
            next = pics_len - 1;
        next = next % pics_len;

        window.history.pushState({}, "", '/gallery/' + next);
        toggleBigImage();
    }

    if (event.keyCode == 112)
        showHelp();
}

function toggleBigImage() {
    var hids = document.getElementsByClassName('hid');
    if (window.location.pathname == '/gallery') {
        for (var i = 0; i < hids.length; i++)
            hids[i].style.display = 'none';
        return;
    }
    else
        for (var i = 0; i < hids.length; i++)
            hids[i].style.display = 'block';

    var id = window.location.pathname.substring(
        window.location.pathname.lastIndexOf('/') + 1
    );
    var el = document.getElementById('image-big');
    var img = document.getElementById(id);
    var href = img.getAttribute('data-big');

    el.setAttribute('data-id', id);
    el.setAttribute('src', href);

    var next = parseInt(id) + 1;
    pics_len = document.getElementsByClassName('gal-img').length;
    if (next < 0)
        next = pics_len - 1;
    next = next % pics_len;

    var img_preload = document.getElementById('img-preload');
    var next_img = document.getElementById(next);
    var next_href = next_img.getAttribute('data-big');
    img_preload.setAttribute('src', next_href);

    pic_name = href.substring(href.lastIndexOf('/') + 1);

    document.getElementsByName('id_')[0].setAttribute('value', pic_name);

    getComments(pic_name);
}

function addEvent(event, func) {
    if (window.addEventListener) {
        window.addEventListener(event, func);
    }
    else {
        window.attachEvent('on' + event, func);
    }
}

addEvent('popstate', function(event) {
    toggleBigImage();
});

addEvent('load', function(event){
    toggleBigImage();
});
