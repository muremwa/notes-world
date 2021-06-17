const secondBtn = document.getElementById('second-btn');

if (secondBtn) {
    secondBtn.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('ogSubmit').disabled = true;
        const url = secondBtn.dataset.secondUrl;
        const form = secondBtn.dataset.formName? document.forms[secondBtn.dataset.formName]: document.forms['gen-form'];

        if (form.checkValidity()) {
            form.action = url;
            form.submit();
        };
    });
};
