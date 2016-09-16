function handleResponseGet(xhr) {
    if (xhr.readyState == 4 && xhr.status == 200) {
        data = JSON.parse(xhr.responseText);
        comment_section = document.getElementById('comments');
        comment_section.innerHTML = '';

        for (var i = 0; i < data.length; i++) {
            author = document.createElement('p');
            author.className = 'author';
            author.innerHTML = data[i]['author'];
            text = document.createElement('p');
            text.className = 'com-text';
            text.innerHTML = data[i]['text'];
            date = document.createElement('p');
            date.className = 'com-date';
            date.innerHTML = data[i]['date'];

            node = document.createElement('div');
            node.appendChild(author);
            node.appendChild(text);
            node.appendChild(date);
            node.appendChild(document.createElement('hr'));

            comment_section.appendChild(node);
        }
    }
}

function getComments(filename) {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', '/comments?filename=' + encodeURIComponent(filename), true);

    xhr.onreadystatechange = function() {
        handleResponseGet(xhr);
    }

    xhr.send();
}

function sendComment() {
    var textarea = document.getElementById('text');
    if (!textarea.value) {
        return;
    }

    var text = textarea.value;
    textarea.value = '';
    var id = document.getElementById('id_').getAttribute('value');
    var csrf = document.getElementById('csrf_token').getAttribute('value');

    var xhr = new XMLHttpRequest();

    var body = 'id_=' + encodeURIComponent(id) + 
               '&csrf_token=' + encodeURIComponent(csrf) + 
               '&text=' + encodeURIComponent(text);

    xhr.open("POST", '/comment', true);
    xhr.setRequestHeader(
        'Content-Type',
        'application/x-www-form-urlencoded'
    );

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            getComments(id);
        }
    }

    xhr.send(body);
}