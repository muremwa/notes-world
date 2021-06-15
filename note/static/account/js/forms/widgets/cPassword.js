const passwords = [...document.getElementsByClassName('js-toogle-password')];
const eyes = [...document.getElementsByClassName('toogle-eye')];
let state = false;


function tooglePasswordView (ps = passwords) {
    ps.forEach((p) => {
        if (p.type) {
            state? p.type = 'password': p.type = 'text';
        };
    });
    state = !state;
};

eyes.forEach((eye) => eye.addEventListener('click', () => tooglePasswordView(passwords)));