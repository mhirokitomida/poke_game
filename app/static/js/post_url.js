// Function to send POST request to the specified 'url' with the 'data' as form fields.
function postToURL(url, data) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    for (var key in data) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = data[key];
        form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();
}