if (!history.pushState) {
    history.pushState = function(one, two, url) {
        var target = url.substring(url.lastIndexOf('/') + 1);
        location.hash = '#' + target;
    }
}

if (!document.getElementsByClassName) {
    document.getElementsByClassName = function(name) {
        return document.querySelectorAll('.' + name);
    }
}

if (!Event.prototype.keyCode) {
    Event.prototype.keyCode = function () {
        return this.which;
    };
}

if (!Event.prototype.preventDefault) {
    Event.prototype.preventDefault = function () {
        this.returnValue = false;
    };
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
        comment.innerHTML = '[' + data[i]['author'] + ']<br>' +
                            data[i]['text'] + '<br>' +
                            '<span class="date">' + data[i]['date'] + '</span>' +
                            '<hr>';
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

function setPreload(current) {
    var next = parseInt(current) + 1;
    pictures = document.getElementsByClassName('gal-img');
    next = next % pictures.length;

    var imagePreload = document.getElementById('img-preload');
    var nextHref = document.getElementById(next).getAttribute('data-big');
    imagePreload.setAttribute('src', nextHref);
}

function getPictureName() {

}

function showBigImage(id, pushHistory) {
    pushHistory = pushHistory || true;
    shade.style.display = 'block';
    cross.style.display = 'block';
    document.getElementById('image-big-div').style.display = 'block';
    if (pushHistory) {
        history.pushState({}, '', '/gallery/' + id);
    }

    var imageBig = document.getElementById('image-big');
    var href = document.getElementById(id).getAttribute('data-big');
    imageBig.setAttribute('data-id', id);
    imageBig.setAttribute('src', href);

    setPreload(id);

    pictureName = href.substring(href.lastIndexOf('/') + 1);
    document.getElementsByName('id_')[0].setAttribute('value', pictureName);

    getComments(pictureName);
}

function setAsBackground() {
    href = document.getElementById('image-big').getAttribute('src');
    document.body.style.backgroundImage = 'url("' + href + '")';
    document.cookie = 'back='+href+'; expires=0; path=/';
}

function hideModals(pushHistory) {
    pushHistory = pushHistory || true;
    document.getElementById('image-big-div').style.display = 'none';
    cross.style.display = 'none';
    shade.style.display = 'none';
    help.style.display = 'none';

    if (pushHistory) {
        history.pushState({}, '', '/gallery');
    }
}

function showHelp() {
    shade.style.display = 'block';
    cross.style.display = 'block';
    help.style.display = 'block';
}

document.onkeydown = function(e) {
    e = e || event
    var key = e.keyCode;
    if (key == 27) {
        hideModals();
        return;
    }
    var el = document.getElementById('image-big-div');
    if (el.style.display != 'none' && el.style.display != '') {
        var imageBig = document.getElementById('image-big');
        var next = parseInt(imageBig.getAttribute('data-id'));
        if (key == 39)
            next++;
        else if (key == 37)
            next--;
        else
            return;

        pictures = document.getElementsByClassName('gal-img');
        if (next < 0)
            next = pictures.length - 1;
        next = next % pictures.length;

        showBigImage(next);
    }

    if (key == 112) {
        showHelp();
        e.preventDefault();
    }
}

function addEvent(e, func) {
    if (addEventListener) {
        addEventListener(e, func);
    }
    else {
        attachEvent('on' + e, func);
    }
}

function getPicId() {
    if (location.hash) {
        return location.hash;
    }

    return location.pathname.substring(location.pathname.lastIndexOf('/') + 1);
}

function changeState() {
    if (location.pathname == '/gallery') {
        hideModals(false);
        return;
    }

    var id = getPicId();
    showBigImage(id, false);
}

addEvent('popstate', changeState);
addEvent('load', changeState);
