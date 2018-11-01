function formControlAdd(name){
    var fields = document.getElementsByTagName(name);

    for(field in fields){
        try {
            fields[field].classList.add("form-control");
        } catch (err){
            // console.log(err)
            continue;
        }
    }
}

var tags = ["input", "textarea", "select", "file", "checkbox"]

$(document).ready(function () {
    for(var x = 0; x < tags.length; x++){
        formControlAdd(tags[x]);
    }
})

// notifications
var notificationsDiv = document.getElementById("new_notifications");
var notificationUrl = notificationsDiv.attributes['data-url'].value;

function newNotifications () { 
    $.ajax({
        type: "GET",
        url: notificationUrl,
        dataType: "json",
        success: function (response) {
            if (response['new']) {
                notificationsDiv.innerText = "("+response['new']+")";
            }
        },
        error: function () {
            console.log('could not load new notifications');
        }
    });
};

$(document).ready( function () {
    newNotifications();
});

// get notifications after every 30 seconds
setInterval(newNotifications, 30*1000);