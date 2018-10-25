// user to send conection requests
$(document).on('click', '.connect-button', function (e) {
    e.preventDefault();
    // get the token
    let button = this
    let form = button.parentElement;
    let url = form.children.connect_url.value;
    let token = form.children.csrfmiddlewaretoken.value;
    
    // send 
    $.ajax( {
        type: "POST",
        url: url,
        data: {
            csrfmiddlewaretoken: token
        },
        success: function (response) {
            console.log(response['sent']);
            if (response['sent']) {
                button.innerText = "sent";
            } else {
                button.innerText = response['state']
            }
        },
        error: function () {
            button.innerText = "error";
        }
    });
});


// user to accepts conection requests
$(document).on('click', '.accept-button', function (e) {
    e.preventDefault();
    // get the token
    let button = this
    let form = button.parentElement;
    let url = form.children.accept_url.value;
    let token = form.children.csrfmiddlewaretoken.value;
    let denyButton = form.children.deny
   
    // send 
    $.ajax( {
        type: "POST",
        url: url,
        data: {
            csrfmiddlewaretoken: token
        },
        success: function (response) {
            if (response['accepted']) {
                denyButton.style.display = "none";
                button.innerText = response['state'];
            };
        },
        error: function (err) {
            console.log(err)
            button.innerText = "error";
        }
    });
});



// user to disconnects users
$(document).on('click', '.disconnect-button', function (e) {
    e.preventDefault();
    // get the token
    let button = this
    let form = button.parentElement;
    let url = form.children.diconnect_url.value;
    let token = form.children.csrfmiddlewaretoken.value;

    // send 
    $.ajax( {
        type: "POST",
        url: url,
        data: {
            csrfmiddlewaretoken: token
        },
        success: function (response) {
            if (response['exited']) {
                button.innerText = response['state'];
            } else {
                button.innerText = response['state'];
            }   
        },
        error: function (err) {
            console.log(err)
            button.innerText = "error";
        }
    });
});


// user to denies users requests
$(document).on('click', '.deny-button', function (e) {
    e.preventDefault();
    // get the token
    let button = this
    let form = button.parentElement;
    let url = form.children.deny_url.value;
    let token = form.children.csrfmiddlewaretoken.value;
    let acceptButton = form.children.approve

    // send 
    $.ajax( {
        type: "POST",
        url: url,
        data: {
            csrfmiddlewaretoken: token
        },
        success: function (response) {
            if (response['denied']) {
                button.innerText = response['state'];
                try {
                    acceptButton.style.display = "none";
                } catch (err) {
                    console.log(err)
                }
            };
        },
        error: function (response) {
            if (response['denied'] == false) {
                button.innerText = response['state'];
            }
        }
    });
});
