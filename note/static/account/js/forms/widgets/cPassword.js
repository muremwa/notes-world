const passwordEyes = [...document.getElementsByClassName('toggle-eye')];

passwordEyes.forEach((eye) => {
    eye.addEventListener('click', () => {
        if ('inputId' in eye.dataset && 'state' in eye.dataset) {
            const input = document.getElementById(eye.dataset.inputId);
            const state = eye.dataset.state;

            if (input && input.hasAttribute('type') && state) {
                input.type = state === '1'? 'password': 'text';
                eye.dataset.state = state === '1'? '0': '1';

                if ('eye' in eye.dataset && 'closedEye' in eye.dataset && eye.hasAttribute('src')) {
                    eye.src = state === '1'? eye.dataset.eye: eye.dataset.closedEye;
                    eye.title = state === '1'? 'click to see password': 'click to hide password'
                }
            }
        }
    })
})