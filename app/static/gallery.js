function expandImage(id) {
    var el = document.getElementById('image-big');
    href = document.getElementById(id).getAttribute('src');
    el.setAttribute('src', href);
    el.setAttribute('data-id', id);

    var hids = document.getElementsByClassName('hid');
    for (var i = 0; i < hids.length; i++) {
        hids[i].style.display = 'block';
    }

    window.history.pushState({}, "", '/' + 'gallery/' + id);
    onResize();
}

function shrinkImage() {
    var hids = document.getElementsByClassName('hid');
    for (var i = 0; i < hids.length; i++) {
        hids[i].style.display = 'none';
    }

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
            shrinkImage();
            return;
        }
        else
            return;
        var nextimg = document.getElementById(next);
        if (nextimg == null) {
            if (next > 0)
                next = 0;
            else
                next = document.getElementsByClassName('gal-img').length - 1;
            nextimg = document.getElementById(next);
        }
        window.history.pushState({}, "", '/gallery/' + next);
        href = nextimg.getAttribute('src');
        el.setAttribute('data-id', next);
        el.setAttribute('src', href);
    }
}

function setImage() {
    var div = document.getElementById('image-big-div');
    var hids = document.getElementsByClassName('hid');
    if (document.location.toString().endsWith('gallery')) {
        for (var i = 0; i < hids.length; i++) {
            hids[i].style.display = 'none';
        }
        return;
    }
    else {
        for (var i = 0; i < hids.length; i++) {
            hids[i].style.display = 'block';
        }
    }
    var id = document.location.toString().substring(document.location.toString().lastIndexOf('/') + 1);
    var el = document.getElementById('image-big');
    var img = document.getElementById(id);
    href = img.getAttribute('src');
    el.setAttribute('data-id', id);
    el.setAttribute('src', href);
    onResize();
}

window.addEventListener('popstate', function(event) {
    setImage();
});

function onResize() {
    var div = document.getElementById('image-big-div');
    if (window.innerWidth > 992) {
        var com = document.getElementById('comments');
        var pic = document.getElementById('image-big');
        
        div.style.height = pic.height + 'px';
        com.style.height = pic.height + 'px';
    }
    else
        div.style.height = null;
}

window.addEventListener('resize', function(event){
    onResize();
});

window.addEventListener('load', function(event){
    setImage();
});