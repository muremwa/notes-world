// notifications
let notifications = 0;

function newNotifications () {
    const notificationsDiv = document.getElementById('new_notifications');
    const notificationsUrl = notificationsDiv? notificationsDiv.dataset.url: null;
    
    if (notificationsDiv && notificationsUrl) {
        const options = {
            url: notificationsUrl,
            responseType: 'json',
            error: () => {},
            success: (response) => {
                const newNotif = response.response['new'];

                if (newNotif !== notifications && newNotif > 0) {
                    notifications = newNotif;
                    notificationsDiv.innerText = `(${newNotif})`;
                };
            }
        };
                
        ajax.get(options);
    };
};

document.addEventListener('readystatechange', () => document.readyState === 'complete'? newNotifications(): void 0);

// get notifications after every 30 seconds
setInterval(newNotifications, 30*1000);