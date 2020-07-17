document.getElementById("photobtn").onclick = function(event){
    event.preventDefault();
    document.getElementById("searitem").style.display = "block";
}

$(function () {
    let nav = $("#nav");
    let navToggle = $("#navToggle");

    navToggle.on("click", function(event){
        event.preventDefault();
        nav.toggleClass("show");
    });


});
