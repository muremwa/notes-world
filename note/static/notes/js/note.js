// conver markdown to html
$(document).ready( function () {
    $(".js-note").each( function () {
        var content = $(this).text();
        var markedContent = marked(content);
        $(this).html(markedContent);
    })
})

let commentArea = document.getElementById("id_comment");
commentArea.placeholder = "add comment here (use '@username' to mention someone '@' '#' are not supported after the username)(markdown is supported)";

function getMentioned () {
    let text = "this @muremwa is just a test @user_4 and @user6";
    // let pattern = "\@\[a-zA-Z0-9_]*"
    let pattern = /@\w*/g;
    let res = text.match(pattern);
    let newRes = [];
    for (r of res) {
        let y = r.split("@")[1]
        let url = "www.facebook.com/" + y;
        let x = '['+y+']('+url+')'
        newRes.push(x)
    }
    console.log(res);
    console.log(newRes);
}

$(document).on("click", '.delete-comment', function (e) {
    e.preventDefault();
    let inpuT = this;
    let deleteUrl = inpuT.attributes["data-url"].value;
    let token = inpuT.parentElement.children.csrfmiddlewaretoken.value;

    $.ajax ( {
        type: "POST",
        url: deleteUrl,
        data: {
            csrfmiddlewaretoken: token
        },
        success: function (response) { 
            if (response['success']) {
                let displayMessage = "<h2 class='text-primary text-center' style='margin-left: 20%'>"+response['message']+"</h2>";
                inpuT.offsetParent.parentElement.innerHTML = displayMessage;
            } else {
                console.log(response['message']);
            }
        },
        error: function (e) {
            console.log("failed to delete comment");
            console.log(e);
        }
    });
})


// editing comments
$(document).on("click", ".edit-comment", function (e) {
    e.preventDefault();
    let text = this.offsetParent.children[1].innerText;
    let commentUrl = this.parentElement.attributes['data-get-comment'].value
    let textAreaDiv = this.offsetParent.children['edit-form'].children[1].children[0];
    textAreaDiv.classList.add("comment-edit");
    textAreaDiv.style.width = "100%";
    
    $.ajax ( {
        type: "GET",
        url: commentUrl,
        success: function (response) {
            if (response['success']) {
                editFiller(response['text'], textAreaDiv);
            } else {
                editFiller(text, textAreaDiv);
            }
        },
        error: function (e) {
            console.log(e);
        }
    });
});


function editFiller (originalValue, whereTo) {
    whereTo.innerText = originalValue;
    whereTo.parentElement.parentElement.style.display = "";
}

$(document).on("click", ".close-edit", function (e) {
    e.preventDefault();
    this.parentElement.style.display = "none";
});