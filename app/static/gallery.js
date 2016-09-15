function expandImage(id) {
    var el = document.getElementById('image-big');
    href = document.getElementById(id).getAttribute('src');
    el.setAttribute('src', href);
    el.setAttribute('data-id', id);
    var el = document.getElementById('image-big-div');
    el.style.display = 'block';
    window.history.pushState({}, "", '/' + 'gallery/' + id);
}

function shrinkImage() {
    var el = document.getElementById('image-big-div');
    el.style.display = 'none';
    window.history.pushState({}, "", '/gallery');
}

document.onkeydown = function(e) {
    var el = document.getElementById('image-big-div');
    if (el.style.display != 'none') {
        var el = document.getElementById('image-big');
        var next = parseInt(el.getAttribute('data-id')) + 1;
        var nextimg = document.getElementById(next);
        if (nextimg == null)
        {
            next = 0;
            nextimg = document.getElementById(next);
        }
        window.history.pushState({}, "", '/gallery/' + next);
        href = nextimg.getAttribute('src');
        el.setAttribute('data-id', next);
        el.setAttribute('src', href);
    }
}

window.addEventListener('popstate', function(event) {
    if (document.location.toString().endsWith('gallery')) {
        var el = document.getElementById('image-big-div');
        el.style.display = 'none';
        return;
    }
    var id = document.location.toString().substring(document.location.toString().lastIndexOf('/') + 1);
    var el = document.getElementById('image-big');
    var img = document.getElementById(id);
    href = img.getAttribute('src');
    el.setAttribute('data-id', id);
    el.setAttribute('src', href);
});
