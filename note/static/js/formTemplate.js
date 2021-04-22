const secondBtn = document.getElementById('second-btn');

if (secondBtn) {
    secondBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const url = secondBtn.dataset['secondUrl'];
        const form = document.forms['gen-form'];

        if (form.checkValidity()) {
            form.action = url;
            form.submit();
        };

    });
};
