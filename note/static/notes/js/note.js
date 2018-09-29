// conver markdown to html
$(document).ready( function () {
    $(".js-note").each( function () {
        var content = $(this).text();
        var markedContent = marked(content);
        console.log(content);
        console.log(markedContent);
        $(this).html(markedContent);
    })
})


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

getMentioned();