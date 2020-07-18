/*$(function () {
    let btn = $("#btn");
    btn.on("click", function(event){
        event.preventDefault();
        $("#age").removeClass("hide");
    });
});*/

document.getElementById('btn').onclick = function(){
      document.getElementById('age').style.display = "none";
      document.getElementById('btn').style.display = "none";
      document.getElementById('ibtn').style.display = "block";
      document.getElementById('iage').style.display = "block";
      document.getElementById('itext').style.display = "block";
      document.getElementById('backbtn').style.display = "block";
}

document.getElementById('writer-btn').onclick = function(){
    document.getElementById('title').style.display = "block";
    document.getElementById('art').style.display = "block";
    document.getElementById('tags').style.display = "block";
    document.getElementById('inp').style.display = "block";
    document.getElementById('btn_btn').style.display = "block";
    document.getElementById('avatarfile').style.display = "block";
    document.getElementById('hiddenframe').style.display = "block";
    document.getElementById('writer-btn').style.display = "none";
}

document.getElementById('photobtn').onclick = function(){
    document.getElementById('inpu').style.display = "block";
    document.getElementById('hf').style.display = "block";
    document.getElementById('af').style.display = "block";
    document.getElementById('ib').style.display = "block";
    document.getElementById('backbtn2').style.display = "block";
    document.getElementById('photobtn').style.display = "none";
}

document.getElementById('backbtn2').onclick = function(){
    document.getElementById('inpu').style.display = "none";
    document.getElementById('hf').style.display = "none";
    document.getElementById('af').style.display = "none";
    document.getElementById('ib').style.display = "none";
    document.getElementById('backbtn2').style.display = "none";
    document.getElementById('photobtn').style.display = "block";
}


document.getElementById('backbtn').onclick = function(){
      document.getElementById('age').style.display = "block";
      document.getElementById('btn').style.display = "block";
      document.getElementById('ibtn').style.display = "none";
      document.getElementById('iage').style.display = "none";
      document.getElementById('itext').style.display = "none";
      document.getElementById('backbtn').style.display = "none";
}

$(function () {
    let nav = $("#nav");
    let navToggle = $("#navToggle");

    navToggle.on("click", function(event){
        event.preventDefault();
        nav.toggleClass("show");
    });

});


document.getElementById("photobtn1").onclick = function(event){
    event.preventDefault();
    document.getElementById("searitem").style.display = "block";
}
