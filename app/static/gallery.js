function expandImage(id) {
    window.history.pushState({}, "", '/' + 'gallery/' + id);
    setImage();
}

function shrinkImage() {
    var hids = document.getElementsByClassName('hid');
    for (var i = 0; i < hids.length; i++)
        hids[i].style.display = 'none';

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
        pics_len = document.getElementsByClassName('gal-img').length;
        if (next < 0)
            next = pics_len - 1;
        next = next % pics_len;
        window.history.pushState({}, "", '/gallery/' + next);
        setImage();
    }
}

function setImage() {
    var hids = document.getElementsByClassName('hid');
    if (document.location.toString().endsWith('gallery')) {
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
    href = img.getAttribute('src');
    el.setAttribute('data-id', id);
    el.setAttribute('src', href);

    pic_name = href.substring(href.lastIndexOf('/') + 1);

    document.getElementById('id_').setAttribute('value', pic_name);

    getComments(pic_name);

    onResize();
}

window.addEventListener('popstate', function(event) {
    setImage();
});

function onResize() {
    var wrp = document.getElementById('big-img-wrapper');
    var pic = document.getElementById('image-big');
    var com = document.getElementById('comments');
    var com_div = document.getElementById('comments-div')
    com.style.height = (com_div.offsetHeight - 130) + 'px';
    if (window.innerWidth > 1300)
    {
        wrp.style.width = null;
        wrp.style.marginLeft = null;
        var gap = wrp.offsetWidth - pic.width;
        if (gap <= 0)
            return;
        wrp.style.width = pic.width + 'px';
        var div = document.getElementById('image-big-div');
        wrp.style.marginLeft = (gap/2) + 'px';
    }
    else {
        wrp.style.marginLeft = null;
        wrp.style.width = null;
    }
    if (window.innerWidth < 992) {
        wrp.style.maxHeight = pic.height + 'px';
    }
    else
        wrp.style.maxHeight = null;
}

window.addEventListener('resize', function(event){
    onResize();
});

window.addEventListener('load', function(event){
    setImage();
});