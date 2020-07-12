document.getElementById('show').onclick = function(){
    x=confirm('Вы уверены?');
}
document.getElementById('shown').onclick = function(){
    x=confirm('Вы уверены?');
}

document.getElementById("photobtn").onclick = function(event){
    event.preventDefault();
    document.getElementById("searitem").style.display = "block";
}
