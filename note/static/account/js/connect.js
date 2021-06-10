// get document cookie
const cookie = new Map([document.cookie.split('=')]);
const token_ = cookie.has('csrftoken')? cookie.get('csrftoken'): '';

const connectionRequestsTypes = {
    ACCEPT: 'a',
    DENY: 'd',
    SEND: 's',
    DISCONNECT: 'di',
    NONE: 'n'
};

function connetionRequests (url, button, token = token_, type_ = connectionRequests.NONE) {
    const options = {
        url,
        headers: [{
            name: 'X-CSRFToken',
            value: token
        }],
        error: () => button.innerText = "error"
    };

    switch (type_) {
        // send connection request
        case connectionRequestsTypes.SEND:
            options.success = (response_) => {
                const response = response_.response;
                response['sent']? button.innerText = "sent": button.innerText = response['state']
            };
            break;

        // accept a connection request
        case(connectionRequestsTypes.ACCEPT):
            options.success = (response_) => {
                const response = response_.response;
                button.innerText = response['state'];

                if (response['accepted']) {
                    const denyButton = button.nextElementSibling;
                    denyButton? denyButton.style.display = "none": void 0;
                };
            };
            break;
        
        // deny a request
        case(connectionRequestsTypes.DENY):
            options.success = (response_) => {
                button.innerText = response_.response['state'];
                button.disabled = true;
                const acceptBtn = button.previousElementSibling;
                acceptBtn? acceptBtn.style.display = 'none': void 0;
            };
            break;
        
        // disconnect from a connection
        case(connectionRequestsTypes.DISCONNECT):
            options.success = (response_) => button.innerText = response_.response['state'];
            break;

        default:
            break;
    }


    ajax.post(options)
};


[...document.getElementsByClassName('js-action-btn')].forEach((bt) => {
    bt.addEventListener('click', (e) => {
        const { actionUrl: actionUrl_, requestType: requestType_ } = e.target.dataset;

        switch (requestType_) {
            case 'send':
                connetionRequests(actionUrl_, e.target, token_, connectionRequestsTypes.SEND);
                break;

            case 'accept':
                connetionRequests(actionUrl_, e.target, token_, connectionRequestsTypes.ACCEPT);
                break;

            case 'deny':
                connetionRequests(actionUrl_, e.target, token_, connectionRequestsTypes.DENY);
                break;

            case 'disconnect':
                connetionRequests(actionUrl_, e.target, token_, connectionRequestsTypes.DISCONNECT);
                break;
        
            default:
                break;
        };

    });
});
