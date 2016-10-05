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

function expandImage(id) {
    window.history.pushState({}, "", '/' + 'gallery/' + id);
    toggleBigImage();
}

function setAsBackground() {
    href = document.getElementById('image-big').getAttribute('src');
    document.body.style.backgroundImage = 'url("' + href + '")';
    document.cookie = "back="+href+"; expires=0; path=/";
}

function hideBigImage() {
    var hids = document.getElementsByClassName('hid');
    for (var i = 0; i < hids.length; i++)
        hids[i].style.display = 'none';
    document.getElementById('help').style.display = 'none';

    window.history.pushState({}, "", '/gallery');
}

document.onkeydown = function(event) {
    var el = document.getElementById('image-big-div');
    if (el.style.display != 'none') {
        var el = document.getElementById('image-big');
        var next = 0;
        if (event.keyCode == 39)
            next = parseInt(el.getAttribute('data-id')) + 1;
        else if (event.keyCode == 37)
            next = parseInt(el.getAttribute('data-id')) - 1;
        else if (event.keyCode == 27) {
            hideBigImage();
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
    else {
        if (event.keyCode == 112) {
            var help = document.getElementById('help');
            var cross = document.getElementById('cross');
            var shade = document.getElementById('shade');
            if (help.style.display != 'block') {
                cross.style.display = 'block';
                shade.style.display = 'block';
                help.style.display = 'block';
            }
            else {
                help.style.display = 'none';
                cross.style.display = 'none';
                shade.style.display = 'none';
            }
        }
    }
}

function toggleBigImage() {
    var hids = document.getElementsByClassName('hid');
    var loc = document.location.toString();
    if (loc[loc.length - 1] == 'y') {
        for (var i = 0; i < hids.length; i++)
            hids[i].style.display = 'none';
        return;
    }
    else
        for (var i = 0; i < hids.length; i++)
            hids[i].style.display = 'block';

    var id = document.location.toString().substring(
        document.location.toString().lastIndexOf('/') + 1
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

    document.getElementById('id_').setAttribute('value', pic_name);

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
