$('document').ready(function(){
    var url = document.URL;
    var ID = url.match(/\/editor\/\w+\/(\d+)/)[1];
    var page = url.match(/\/editor\/(\w+)\//)[1];


    //Really, REALLY, ugly solutions, but it works.....
    /*if (page == "general") {
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
    }*/

    //console.log(routes);

    var tour = document.getElementById(ID);
    var temp = tour.getElementsByTagName("ul")[0];
    var list = temp.getElementsByTagName("li");


    for (var i = 0; i < list.length; i++) {
	if (page == list[i].children[1].id) {
	    list[i].children[1].className = "editor-btn active";
	}
	else {
	    list[i].children[1].className = "editor-btn";
	}
    }
});
