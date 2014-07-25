$('document').ready(function(){
    var url = document.URL;
    var ID = url.match(/\/editor\/\w+\/(\d+)/)[1];
    var page = url.match(/\/editor\/(\w+)\//)[1];

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
