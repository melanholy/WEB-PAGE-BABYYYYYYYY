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
    var csrf = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    var data = {'id_': id, 'csrf_token': csrf, 'text': text};

    textarea.value = '';

    ajaxSend(
        '/comment', 'POST', data,
        function(xhr) {
            if (xhr.responseText[0] !== '[')
                document.write(xhr.responseText);
            else
                addCommentsToDocument(xhr);
        }
    );
}

function showBigImage(id, pushHistory=true) {
    document.getElementById('shade').style.display = 'block';
    document.getElementById('cross').style.display = 'block';
    document.getElementById('image-big-div').style.display = 'block';
    if (pushHistory) {
        window.history.pushState({}, '', '/gallery/' + id);
    }

    var imageBig = document.getElementById('image-big');
    var href = document.getElementById(id).getAttribute('data-big');
    imageBig.setAttribute('data-id', id);
    imageBig.setAttribute('src', href);

    var next = parseInt(id) + 1;
    pics_len = document.getElementsByClassName('gal-img').length;
    next = next % pics_len;

    var imgPreload = document.getElementById('img-preload');
    var nextHref = document.getElementById(next).getAttribute('data-big');
    img_preload.setAttribute('src', next_href);

    pic_name = href.substring(href.lastIndexOf('/') + 1);
    document.getElementsByName('id_')[0].setAttribute('value', pic_name);

    getComments(pic_name);
}

function setAsBackground() {
    href = document.getElementById('image-big').getAttribute('src');
    document.body.style.backgroundImage = 'url("' + href + '")';
    document.cookie = 'back='+href+'; expires=0; path=/';
}

function hideModals(pushHistory=true) {
    document.getElementById('image-big-div').style.display = 'none';
    document.getElementById('cross').style.display = 'none';
    document.getElementById('shade').style.display = 'none';
    document.getElementById('help').style.display = 'none';

    if (pushHistory) {
        window.history.pushState({}, '', '/gallery');
    }
}

function showHelp() {
    document.getElementById('shade').style.display = 'block';
    document.getElementById('cross').style.display = 'block';
    document.getElementById('help').style.display = 'block';
}

document.onkeydown = function(event) {
    var el = document.getElementById('image-big-div');
    if (el.style.display != 'none') {
        var imageBig = document.getElementById('image-big');
        var next = parseInt(imageBig.getAttribute('data-id'));
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

        showBigImage(next);
    }

    if (event.keyCode == 112)
        showHelp();
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
    if (window.location.pathname == '/gallery' ||
        window.location.pathname == '/gallery/') {
        hideModals(false);
        return;
    }

    var id = window.location.pathname.substring(
        window.location.pathname.lastIndexOf('/') + 1
    );
    showBigImage(id, false);
});

addEvent('load', function(event){
    if (window.location.pathname == '/gallery' ||
        window.location.pathname == '/gallery/') {
        return;
    }

    var id = window.location.pathname.substring(
        window.location.pathname.lastIndexOf('/') + 1
    );
    showBigImage(id, false);
});
