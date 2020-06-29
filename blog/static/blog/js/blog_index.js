document.getElementById('a').onclick = function(){
    document.getElementById('bi43').style.display = "block";
    document.getElementById('bi44').style.display = "block";
    document.getElementById('bi18').style.display = "block";
    document.getElementById('bi19').style.display = "block";
    document.getElementById('bi110').style.display = "block";
    document.getElementById('a').style.display = "none";
}

$(function () {
    let nav = $("#nav");
    let navToggle = $("#navToggle");

    navToggle.on("click", function(event){
        event.preventDefault();
        nav.toggleClass("show");
    });

});
