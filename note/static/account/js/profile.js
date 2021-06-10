/* 
    Open and delete notifications
*/

// get document cookie
const profileCookie = new Map([document.cookie.split('=')]);
const profileToken_ = profileCookie.has('csrftoken')? profileCookie.get('csrftoken'): '';


// open a notification
[...document.getElementsByClassName('notification-open')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        const { newLocation, readUrl } = event_.target.dataset;
        const errorOpening = () => event_.target.innerText = 'error';

        const options = {
            url: readUrl,
            responseType: 'json',
            headers: [{
                name: 'X-CSRFToken',
                value: profileToken_
            }],
            error: errorOpening,
            success: (response_) => response_.response['success']? window.location = newLocation: errorOpening()
        };

        ajax.post(options);

    });
});


// delete a notification
[...document.getElementsByClassName('notification-delete')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        const { deleteUrl, notificationDivId } = event_.target.dataset;
        const errorDeleting = () => event_.target.innerText = 'error';
        const notificationDiv = document.getElementById(notificationDivId);
        
        const options = {
            url: deleteUrl,
            responseType: 'json',
            headers: [{
                name: 'X-CSRFToken',
                value: profileToken_
            }],
            error: errorDeleting,
            success: (response_) => {
                if (response_.response['success']) {
                    if (notificationDiv) {
                        notificationDiv.remove();
                    } else {
                        event_.target.innerText = 'deleted'
                        event_.target.disabled = true;
                    };
                } else {
                    if (response_.response['responseText']) {
                        event_.target.innerText = response_.response['responseText']
                        event_.target.disabled = true;
                    } else {
                        errorDeleting();
                    };
                };
            }
        };

        ajax.post(options);
    });
});
