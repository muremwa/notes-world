// reply.js
$(document).ready( function() {
    let replyArea = document.getElementById("id_comment");
    replyArea.rows = 3;
    replyArea.placeholder = "reply to the comment above";
})

// editing replies supprt
$(document).on('click', '#edit_reply', function (e) {
    e.preventDefault();
    let url = this.parentElement.attributes['data-reply-url'].value;
    let x = this.parentElement.parentElement.children;
    let form = x['edit_reply_form'].children[1].children[0];

    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            if (response['success']) {
                x['edit_reply_form'].style.display = "";
                form.innerText = response['text'];
                form.rows = 2
            }
        },
        error: function (e) {
            console.log("an error occured");
        }
    });
});

$(document).on('click', '.abort', function (e) {
    e.preventDefault();
    this.parentElement.parentElement.style.display = "none";
});