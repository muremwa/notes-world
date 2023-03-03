/* 
    Open and delete notifications
*/

// get document cookie
const profileCookie = new Map([document.cookie.split('=')]);
const profileToken_ = profileCookie.has('csrftoken')? profileCookie.get('csrftoken'): '';


// open a notification
[...document.getElementsByClassName('notification-open')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        event_.target.innerText = 'opening...';
        const { newLocation, readUrl } = event_.target.dataset;
        const errorOpening = () => {
            event_.target.innerText = 'error opening notification';
            event_.target.disabled = true;
        };

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
                    }
                } else {
                    if (response_.response['responseText']) {
                        event_.target.innerText = response_.response['responseText']
                        event_.target.disabled = true;
                    } else {
                        errorDeleting();
                    }
                }
            }
        };

        ajax.post(options);
    });
});


// Ensure correct values are sent when deleting bulk notifications
function bulkClean (home, away, larger, ogDel, r = false) {
    const home_value = home.value? home.value === 'all'? 1000: parseInt(home.value): 0;
    const away_value = away.value? away.value === 'all'? 1000: parseInt(away.value): 0;

    if (r) {
        ogDel.disabled = true;
    } else {
        if (larger) {
            home_value > away_value? ogDel.disabled = false: ogDel.disabled = true;
        } else {
            away_value > home_value? ogDel.disabled = false: ogDel.disabled = true;        
        }
    }
}


const formOg = document.getElementById('notifications-delete-form');
const bDelBtn = document.getElementById('notifications-delete-btn');
const from = document.getElementById('from_date');
const to = document.getElementById('to_date');

if (formOg && bDelBtn && from && to) {
    from.addEventListener('change', () => bulkClean(from, to, false, bDelBtn));
    to.addEventListener('change', () => bulkClean(to, from, true, bDelBtn));
    formOg.addEventListener('reset', () => bulkClean(to, from, true, bDelBtn, true));
}