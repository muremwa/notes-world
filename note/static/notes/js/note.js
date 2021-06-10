// convert markdown to html
document.addEventListener('readystatechange', () => {
    if (document.readyState === 'complete') {
        const noteDiv = document.getElementById('note-top');

        if (noteDiv) {
            const paintEvent = new Event('paint');
            noteDiv.addEventListener('paint', (e) => loadNoteNav(e.target));
            noteDiv.innerHTML = marked(noteDiv.innerHTML);
            noteDiv.dispatchEvent(paintEvent);
        };
    };
});

// get document cookie
const noteCookie = new Map([document.cookie.split('=')]);
const noteToken_ = noteCookie.has('csrftoken')? noteCookie.get('csrftoken'): '';

// deleting comments async
[...document.getElementsByClassName('delete-comment')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        event_.target.innerText = 'deleting comment...'
        const { deleteUrl, commentDivId } = event_.target.dataset;
        const commentDiv = document.getElementById(commentDivId);
        const errorDeleting = () => event_.target.innerText = 'could not delete comment';

        const options = {
            url: deleteUrl,
            responseType: 'json',
            headers: [{
                name: 'X-CSRFToken',
                value: noteToken_
            }],
            error: errorDeleting,
            success: (response_) => response_.response['success']? commentDiv.remove(): errorDeleting
        };

        ajax.post(options);
    });
});


function toggleForm (divId, open) {
    const form = document.getElementById(divId);
    const txt = document.getElementById(`${divId}-textarea`);

    if (form) {
        form.style.display = open? 'none': '';
        txt && !open? txt.focus(): form.reset();
    };
};


// open comment edit form
[...document.getElementsByClassName('edit-comment')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        const { editFormId } = event_.target.dataset;
        editFormId? toggleForm(editFormId, false): void 0;
    });
});


// close comment edit form
[...document.getElementsByClassName('close-edit')].forEach((element) => {
    element.addEventListener('click', (event_) => {
        const { closeId } = event_.target.dataset;
        closeId? toggleForm(closeId, true): void 0;
    })
})