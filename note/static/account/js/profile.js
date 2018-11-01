// open notification
$(document).on('click', '.notification', function (e) {
    let notificationDiv = this;
    let newLocationUrl = notificationDiv.attributes['data-location'].value;
    let markNotificationAsReadUrl = notificationDiv.attributes['data-read-url'].value;
    let token = notificationDiv.parentElement.children.csrfmiddlewaretoken.value;

    $.ajax({
        type: "POST",
        url: markNotificationAsReadUrl,
        data: {
            csrfmiddlewaretoken: token
        },
        success: function (result) {
            if (result['success']) {
                console.log('marked as open')
                window.location = newLocationUrl;
            }
        },
        error: function () {
            console.log('error: could not open notification');
        }
    });
});

