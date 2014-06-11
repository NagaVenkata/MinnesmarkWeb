$('document').ready(function(){
    insertInput();
});

function saveInput() {
    localStorage.setItem("username", document.getElementById("username").value);
    localStorage.setItem("email", document.getElementById("email").value);
    localStorage.setItem("firstname", document.getElementById("firstname").value);
    localStorage.setItem("lastname", document.getElementById("lastname").value);
}

function insertInput() {
    document.getElementById("username").value = localStorage.getItem("username");
    document.getElementById("email").value = localStorage.getItem("email");
    document.getElementById("firstname").value = localStorage.getItem("firstname");
    document.getElementById("lastname").value = localStorage.getItem("lastname");
}