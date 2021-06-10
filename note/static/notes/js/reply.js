function toggleForm (divId, open) {
    const form = document.getElementById(divId);
    const txt = document.getElementById(`${divId}-textarea`);

    if (form) {
        form.style.display = open? 'none': '';
        txt && !open? txt.focus(): form.reset();
    };
};


// open comment edit form
[...document.getElementsByClassName('edit-reply')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        const { editFormId } = event_.target.dataset;
        editFormId? toggleForm(editFormId, false): void 0;
    });
});


// close comment edit form
[...document.getElementsByClassName('abort')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        const { closeId } = event_.target.dataset;
        closeId? toggleForm(closeId, true): void 0;
    })
})