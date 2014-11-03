$('document').ready(function(){
    
	
	//function called when clicked on publish a trial
    $("#publish_trail").on('click',function(){
    	
    	publishJsonFile($(this));
    	
    });
    
	//load the map 
    loadMap();
    
    //print the map
    $("#printMap").on('click',function() {
    	
    	
    	var dataUrl=[];
    	var i=0;

    	$("#map-canvas canvas").filter(function(){
    	 
    	 dataUrl.push(this.toDataURL("image/png"));  		
    	});
    	
    	var DocumentContainer = document.getElementById('map-canvas');            	
    	var DocumentContainer_temp=$(DocumentContainer).clone();
    	            	
    	$(DocumentContainer_temp).find('canvas').each(function () {            		
    	 $(this).replaceWith('<img title="abc" src="' +  dataUrl[i] + '" style="position: absolute; left: 0px; top: 0px; width: 256px; height: 256px;">');
    	 i++;
    	}); 

    	var WindowObject = window.open('', "PrintMap","width=740,height=325,top=200,left=250,resizable=yes");

    	WindowObject.document.writeln(DocumentContainer_temp.html());
    	      
    	WindowObject.document.close();
    	WindowObject.focus();
    	WindowObject.print();
    	WindowObject.close();

    	
    	/*console.log("Entered map print");
    	var contents = document.getElementById("map-canvas");    
    	
    	var mapWindow = window.open("","","width=800,height=800");
    	mapWindow.document.write(contents.innerHTML);
    	mapWindow.document.close();
    	mapWindow.print();*/
    	
    	    	
    });
    
    
    //print markers
    $("#printMarker").on('click',function() {
    	
    	//prints the markers
    	printMarkers();
    	
    });
    
    

});

getIDfromURL = function(){
    patt = new RegExp(/\/editor\/\w*\/(\d+)/)
    id = patt.exec(document.URL);
    return id[1];
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};


//Opens the window with file options
function publishJsonFile(e){
    
    var $bg = $('.publish');
    var $upload = $('.publish-file');
    var $btnAbort = $('.publish-abort');
    var $btn = $('.publish');

    $btnAbort.on('click',function(){
        $bg.fadeOut();
        $upload.fadeOut();
        $("input[name='publish']").prop('disabled',false);
        $("input[name='publish']").prop('checked',false);
    });
    $btn.on('click',function(){
        publishSelectedTrail();
            $bg.fadeOut();
            $upload.fadeOut();
            $("input[name='publish']").prop('disabled',false);
            $("input[name='publish']").prop('checked',false);

    })

    var top = ($(window).height()/2) - ($upload.outerHeight()/2+100);
    var left = ($(window).width()/2) - ($upload.outerWidth()/2-150);
    $upload.css({top:top,left:left});

    $bg.fadeIn();
    $upload.fadeIn();

}

//publish the trail
function publishSelectedTrail(){
	
	
	var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                console.log(csrftoken);
            }
        }
    });
	
	
    var stationsMedia = $('.stationsCheckboxes');
    var markersMedia = $('.markersCheckboxes');
    
	
    var media={};
    var stations = []
    
    for(var i=0;i<stationsMedia.length;i++) {
    	
    	//console.log(markersMedia[i].checked);
    	var station_id = {
    				
    				"id":stationsMedia[i].id,
    				"checked":stationsMedia[i].checked
    				
    		};
    		stations.push(station_id);
    		
    }
    
    media['stations_media'] = stations;
    
    var markers = []
    
    for(var i=0;i<markersMedia.length;i++) {
    	
    	//console.log(markersMedia[i].checked);
    	var marker_id = {
    				
    				"id":markersMedia[i].id,
    				"checked":markersMedia[i].checked
    				
    		};
    		markers.push(marker_id);
    		
    }
    
    
    
    media['markers_media'] = markers;
    
    	
	var request = $.ajax({
		url: "/editor/publish/"+$("input[name='publish']").val()+"/",
        type: "POST",
        dataType:"json",
        data: JSON.stringify(media),
        contentType: "application/json;charset=utf-8",
       
        success: function(res){
            console.log("SUCCESS");
            $("#publish_trail").html("Dra tillbaka publicering");
            //alert("Hi");
            //console.log(res);
         }
    }); 
	
	 request.done(function(msg) {
         console.log(msg);
     });

     request.fail(function(jqXHR, textStatus) {
         //alert( "Request failed: " + textStatus );
     });
}


//show the map 
function loadMap() {
	
	
	var editor_data = {}
    var route_id = getIDfromURL();
    var request = $.ajax({
        url: "/editor/getRoute/"+route_id,
        type: "GET",
        datatype:JSON,
        contentType: "application/json;charset=utf-8",
        success: function(res){
            console.log(res);
            
            if(res != "ERROR"){
            	
                showMap(res)
            }else{
            	alert("res in error "+res);
                $('.fadeBGShow').remove();
            }
        }
    });

	
	
	
}

function showMap(data) {
	
	var load_stations = data["stations"];
	var load_polylines = data["points"]
    
		
    initialLocation = new google.maps.LatLng(load_polylines[0].latitude,load_polylines[0].longitude); // Drottningholm, Stockholm
	
	var mapOptions = {
            center: initialLocation,
            //panControl: false,
            mapTypeControlOptions: {
                mapTypeId: [
                google.maps.MapTypeId.ROADMAP,
                google.maps.MapTypeId.TERRAIN,
                google.maps.MapTypeId.HYBRID,
                google.maps.MapTypeId.SATELLITE
                ],
                position: null,
                style: null
            },
            streetViewControl: false,
            zoom: 15,
            zoomControl: false,
            zoomOptions: null,
            disableDefaultUI: true,
            draggable:false,
            scrollwheel:false,
            navigationControl:false,
            mapTypedControl:false,
            scaleControl:false,
            zoomControl:false,
            disableDoubleClickZoom: true

        };
	
	var locations = [59.321693,17.886825];
	
	var printmap =  new google.maps.Map(document.getElementById('map-canvas'),mapOptions);
	
	//alert(printmap);
	
	var polyOptions = {
            clickable: false,        // handle mouse events
            draggable: false,       // line can be moved
            editable: false,         // adds control points
            geodesic: false,        // straight or curved lines
            //icons,                // icons along the line
            map: printmap,               // map to display on
            //path,                 // points on the line
            suppressUndo: true,     // undo button when moving line
            strokeColor: '#000000', // color
            strokeOpacity: 1.0,     // opacity between 0.0 and 1.0
            strokeWeight: 3,        // width in pixels
            visible: true,           // visible on map
            //zIndex: 1000               // compared to other polys

            // CUSTOM PROPERTIES
        };

        var polyLine = new google.maps.Polyline(polyOptions);

	
	var index = 1;
	
	for(var i = 0; i < load_polylines.length;i++ ){
    	
		var linePos = new google.maps.LatLng(load_polylines[i].latitude,load_polylines[i].longitude);
    	
        for(var j = 0; j < load_stations.length; j++){
            if(load_stations[j].index == load_polylines[i].index){
            	
            	
            	var customImage = {
         	           url: '/static/editor/img/station-on-map.png',
         	           // The origin for this image is 0,0.
         	           origin: new google.maps.Point(0,0),
         	           // The anchor for this image is the base of the flagpole at 0,32.
         	           anchor: new google.maps.Point(21, 22)
         	    };
         	    var station = new MarkerWithLabel({
         	        // DEFAULT PROPERTIES
         	        //anchorPoint,          // offset of InfoWindow from marker pos
         	        animation: google.maps.Animation.DROP, // when added to map
         	        clickable: false,        // handle mouse events
         	        crossOnDrag: false,      // cross beneath marker on drag
         	        //cursor,               // what mouse cursor to show on hover
         	        draggable:false,         // marker can be moved
         	        flat: false,            // marker shadow
         	        icon:customImage,       // foreground icon
         	        map: printmap,               // map to display on
         	        optimized: false,       // render many markers as one,
         	                                    // not supported by MarkerWithLabel
         	        position: linePos,     // latlng
         	        raiseOnDrag: false,     // raise/lower marker on drag
         	        //shadow,               // what shadow image to show
         	        //shape,                // 
         	        //title,                // rollover text
         	        visible: true,          // visible on map
         	        zIndex: 1000,               // compared to other markers

         	        // MARKERWITHLABEL PROPERTIES
         	        //crossImage,
         	        //handCursor,
         	        labelAnchor: new google.maps.Point(-25, 17),
         	        labelClass: "labels",       // the CSS class for the label
         	        labelContent: (index).toString(),
         	        labelInBackground: false,
         	        //labelStyle,
         	        labelVisible: true,         // visible if marker is

         	        // CUSTOM PROPERTIES
         	        pathIndex: index
         	    });
         	    
         	    index+=1;
            }
            
            //alert(load_polylines[i].index);
            
                            
                //alert(load_polylines[i].index);

                polyLine.getPath().setAt(load_polylines[i].index,linePos);
                
                //alert(polyLine.getPath().setAt(load_polylines[i].index,linePos));
        }
	}
	
    
    google.maps.event.trigger(printmap, 'resize');
}

//prints markers
function printMarkers() {
	
	
	var route_id = getIDfromURL();
	
	var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                console.log(csrftoken);
            }
        }
    });
	
	var request = $.ajax({
		url: "/editor/publish/"+route_id+"/",
        type: "GET",
        contentType:'application/pdf',
        success: function(res){
            console.log("SUCCESS");
            //console.log(res);
            //var pdf = window.open();
            //window.document.write(res);
            //window.print()
            var pdf = new Object();
            pdf = res;
            console.log(res.pdf_url);
            //window.document.write(res);
            //window.document.close();
            //console.log(pdf);
            //pdf.print();
            /*var pdfContent = $("#pdf").parent();
            var newPdf = "<embed src='/static/temp/Umapathi/markers.pdf' id='pdf'>";
            $("#pdf").remove();
            pdfContent.append(newPdf);
            pdfContent.print();*/
            
            /*var pdf = ["/static/temp/Umapathi/markers.pdf"];
            
            var pdfWindow = new Array();
            
            pdfWindow = window.open(pdf);
            pdfWindow.print();*/
            
            
            
            
            
            //console.log($("#pdf"));
            
            /*$('#pdf').attr('src','/static/temp/Umapathi/markers.pdf');
            
            var printPDF = window.frames["pdf"].focus();
            window.frames["pdf"].print();
            
            
            //console.log($('#pdf').contents());
            
            //printPDF.focus();
            
            //var pdfprint = setTimeout(printPDF.print(),50);
            
            //window.clearTimeout(pdfprint);
            
            //window.print();
            
            
            //printPDF.document.write('<body onload="window.print()">'+$('#pdf').contents()+'</body>');
            //printPDF.document.close();
            
            //console.log($('#pdfContent')) */
            
            console.log(window.navigator.userAgent);
            var curr_browser = window.navigator.userAgent;
            if(curr_browser.indexOf('Firefox')>-1)
               window.open(res.pdf_url);
            else {
               $('#pdf').attr('src',res.pdf_url);
               $('#pdfContent').hide();
            }   
            
            //alert("Hi");
            //console.log(res);
         }
	    
	     
	
    });
	
    var curr_browser = window.navigator.userAgent;
	
	if(curr_browser.indexOf('Firefox')<=-1) {
	   setTimeout(function() {
		 
		 var printPDF = window.frames["pdf"].focus();
		 window.frames["pdf"].print();},500);
	}   

}

