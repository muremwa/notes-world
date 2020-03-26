// open notification
$(document).on('click', '.notification', function (e) {
    let notificationDiv = this;
    let newLocationUrl = notificationDiv.attributes['data-location'].value;
    let markNotificationAsReadUrl = notificationDiv.attributes['data-read-url'].value;
    let token = notificationDiv.parentElement.parentElement.children.csrfmiddlewaretoken.value;

    $.ajax({
        type: "POST",
        url: markNotificationAsReadUrl,
        data: {
            csrfmiddlewaretoken: token
        },
        success: function (result) {
            if (result['success']) {
                window.location = newLocationUrl;
            }
        },
        error: function () {
            console.log('error: could not open notification; check your connection');
        }
    });
});
var t;

// delete notifications
$(document).on ('click', '.notification-delete', function () {
    const parent = this.parentElement;
    const url = parent.attributes['data-del-url'].value;
    const token = parent.children.csrfmiddlewaretoken.value;

    $.ajax({
        type: "POST",
        url: url,
        data: {
            csrfmiddlewaretoken: token,
        },
        success: function (response) {
            if (response['success']) {
                parent.parentElement.remove();
            };
        },
        error: function (response) {
            console.log("huge fucking error")
            console.log(response.responseText);
        }
    });

});
