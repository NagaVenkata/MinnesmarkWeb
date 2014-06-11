$('document').ready(function(){
    var url = document.URL;
    var page = url.match(/\/editor\/(\w+)/)[1];

    //Really, REALLY, ugly solutions, but it works.....
    if (page == "general") {
	document.getElementById("general").className = "editor-btn active";
	document.getElementById("stations").className = "editor-btn";
	document.getElementById("media").className = "editor-btn";
	document.getElementById("publish").className = "editor-btn";
    }  
    else if (page == "stations") {
	document.getElementById("general").className = "editor-btn";
	document.getElementById("stations").className = "editor-btn active";
	document.getElementById("media").className = "editor-btn";
	document.getElementById("publish").className = "editor-btn";
    }
    else if (page == "media") {
	document.getElementById("general").className = "editor-btn";
	document.getElementById("stations").className = "editor-btn";
	document.getElementById("media").className = "editor-btn active";
	document.getElementById("publish").className = "editor-btn";
    }    
    else if (page == "publish") {
	document.getElementById("general").className = "editor-btn";
	document.getElementById("stations").className = "editor-btn";
	document.getElementById("media").className = "editor-btn";
	document.getElementById("publish").className = "editor-btn active";
    }
    else {
	document.getElementById("general").className = "editor-btn";
	document.getElementById("stations").className = "editor-btn";
	document.getElementById("media").className = "editor-btn";
	document.getElementById("publish").className = "editor-btn";
    }
});