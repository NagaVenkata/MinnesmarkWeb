$('document').ready(function(){
    var url = document.URL;
    var text = "Välj eller skapa ny rundvandring till vänster";
    if (url.indexOf("general") >= 0) {
	text = "1. Bestäm namn och startmedia";
    }
    else if (url.indexOf("stations") >= 0) {
	text = "2. Lägg till stationer på kartan";
    }
    else if (url.indexOf("media") >= 0) {
	text = "3. Lägg till media";
    }
    else if (url.indexOf("publish") >= 0) {
	text = "4. Publicera, skriv ut och färdigställ";
    }
    document.getElementById("headlineName").innerHTML = text;
});
