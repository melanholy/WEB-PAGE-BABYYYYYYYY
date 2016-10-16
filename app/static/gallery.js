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

function createImageBig() {
    var imageBig = document.createElement('img');
    imageBig.id = 'image-big';
    imageBig.class = 'img-responsive';
    imageBig.alt = 'Большое изображение';
    imageBig.style.cssText = 'margin-left: -4px; \
                              vertical-align: middle; \
                              display: inline-block; \
                              max-height: 100%; max-width: 100%;\
                              background-image: url(/static/spinner.gif); \
                              background-repeat: no-repeat; \
                              background-position: center;';
    return imageBig;
}

function createImgPreload() {
    var imagePreload = document.createElement('img');
    imagePreload.style.display = 'none';
    imagePreload.alt = 'если вы это читаете, сделайте мне бутерброд';
    imagePreload.id = 'img-preload';

    return imagePreload;
}

function setPreload(current) {
    var next = parseInt(current) + 1;
    pictures = document.getElementsByClassName('gal-img');
    next = next % pictures.length;

    var imagePreload = document.getElementById('img-preload');
    if (imagePreload === null) {
        imagePreload = createImgPreload();
        var wrapper = document.getElementById('big-img-wrapper');
        wrapper.appendChild(imagePreload);
    }
    var nextHref = document.getElementById(next).getAttribute('data-big');
    imagePreload.setAttribute('src', nextHref);
}

function showBigImage(id, pushHistory=true) {
    document.getElementById('shade').style.display = 'block';
    document.getElementById('cross').style.display = 'block';
    var imageDiv = document.getElementById('image-big-div');
    imageDiv.style.display = 'block';
    if (pushHistory) {
        window.history.pushState({}, '', '/gallery/' + id);
    }

    var imageBig = document.getElementById('image-big');
    var wrapper = document.getElementById('big-img-wrapper');
    if (imageBig !== null) {
        wrapper.removeChild(imageBig);
    }
    imageBig = createImageBig();
    wrapper.appendChild(imageBig);

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
    if (event.keyCode == 27) {
        hideModals();
        return;
    }
    var el = document.getElementById('image-big-div');
    if (el.style.display != 'none' && el.style.display != '') {
        var imageBig = document.getElementById('image-big');
        var next = parseInt(imageBig.getAttribute('data-id'));
        if (event.keyCode == 39)
            next++;
        else if (event.keyCode == 37)
            next--;
        else
            return;

        pictures = document.getElementsByClassName('gal-img');
        if (next < 0)
            next = pictures.length - 1;
        next = next % pictures.length;

        showBigImage(next);
    }

    if (event.keyCode == 112) {
        event.preventDefault();
        showHelp();
    }
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
