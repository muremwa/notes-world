function formControlAdd(name){
    var fields = document.getElementsByTagName(name);

    for(field in fields){
        try {
            fields[field].classList.add("form-control");
        } catch (err){
            // console.log(err)
            continue;
        }
    }
}

var tags = ["input", "textarea", "select", "file", "checkbox"]

$(document).ready(function () {
    for(var x = 0; x < tags.length; x++){
        formControlAdd(tags[x]);
    }
})