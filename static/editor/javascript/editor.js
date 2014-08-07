/**
 * Created by ante on 2014-03-27.
 */
var media=0;
var newMedia=null;

//require('/static/editor/javascript/build/pdfmake.js');

$('document').ready(function(){
    /*
        Get Active and display menu on load
     */
	
	
    $('.tour-list li').each(function(){
        if($(this).hasClass('active')){
            $(this).find('.tour-menu').show();
            $(this).find('.typcn-chevron-right').addClass('rotate90');
        }
    })
    $('.tour-list li').on('click',function(e){
        /*
            If Not has Active class, Hide all tour-menus
            and display the clicked one
         */
    	
        if(!$(this).hasClass('active')){
	    document.location.pathname = "editor/general/" + $(this)[0].id;
            $(".tour-list li").each(function() {
                $(this).removeClass('active');
                $(this).find('.typcn-chevron-right').removeClass('rotate90');
            });
            $(".tour-menu").each(function() {
                $(this).slideUp();
            });
            $(this).addClass('active');
            $(this).find('.tour-menu').slideDown();
            $(this).find('.typcn-chevron-right').addClass('rotate90');
        }
        /*
            If active and showing
            only hide the one clicked
         */
        else{
            $(this).find('.tour-menu').slideUp();
            $(this).removeClass('active');
            $(this).find('.typcn-chevron-right').removeClass('rotate90');
        }
    });
    
    
    var elements = $('.media-opt');
    var option;
    
    media = elements;
    
    //console.log(elements.length);
    
    
    if(elements.length>=1) {
    	for(var i=0;i<elements.length;i++) {
    	option = elements[i].value;
    	console.log(elements[i]);
    	if(option!=1 && option!=2 && option!=3) {
        	
    		elements[i].disabled = true;
        	
          }
    	}
    } 	
    
    
    
    /*$('.media-files').on("sortchange",function(event,ui){
    	
    	console.log(event);
    	console.log(ui);
    	$( '.media-files' ).sortable( "refreshPositions" );
    	
    });*/
    
    
    
    
    $('.media-opt').on('click',function(){
        createMediaOptionsWindow($(this));
    });

    //function is called when clicked on add media button
    $('.add-media').on('click',function(){
       //alert($('.add-media').attr("name"));	
       var media_type = $('.add-media').attr("name");
       //alert(media_type);
       /*var elements = $('.media-opt');
       
       var filename = null;
       
       
       if(media_type=="None" && elements.length>0 && (filename.localeCompare("m4a")==-1 && filename.localeCompare("mp3")==-1 && filename.localeCompare("m4v")==-1))
    	   alert("choose media type for uploaded file");
       else*/
           openFileUpload($(this));
    });
    
    //function called when clicked on publish a trial
    $("input[name='publish']").on('click',function(){
    	
    	//var w = window.open("about:blank");
    	//w.document.write("/Users/Umapathi/Desktop/text.pdf");
    	//w.print();
    	publishJsonFile($(this));
    	$("input[name='publish']").prop('disabled',true);	
     });
    
    
    $('#print').on('click',function(){
    	
    	publishTrail();
    });
    
   
    $('#hideMenu').on('click', function(){
	if (document.getElementById("contentDiv").className == "column two-thirds") {
	    document.getElementById("menuDiv").style.display = 'none';
	    document.getElementById("contentDiv").className = "column half";
	}
	else {
	    //document.getElementById("menuDiv").className = "column third";
	    document.getElementById("menuDiv").style.display = 'block';
	    document.getElementById("contentDiv").className = "column two-thirds";
	}
    });
});

function addmedia() {
	
	var media = $('.media-opt');
	
	
    var markers = []
    
    for(var i=0;i<media.length;i++) {
    	
    	var option = media[i].value;
    	
    	if(option=="None")
    		option=0;
    		
    	
    	 var marker_id = {
    				
    				"id":media[i].name,
    				"option":option
    				
    		};
    		markers.push(marker_id);
    }
    
    var markers_media={};
    
    markers_media['markers_media'] = markers;
    
    console.log(JSON.stringify(markers_media));
   
    var route_id = $('.startmedia-wrapper').attr("id");
    var marker_id = $('.media-files').attr("id");
    
    
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
		url: "/editor/media/marker/"+route_id+"/"+marker_id+"/",
        type: "POST",
        dataType:"json",
        data: JSON.stringify(markers_media),
        contentType: "application/json;charset=utf-8",
       
        success: function(res){
            console.log("SUCCESS");
            window.location.href="/editor/media/"+route_id+"/";
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

function exit() {
	
	var route_id = $('.startmedia-wrapper').attr("id");
	
	
	
	if(newMedia==null) {
		
		window.location.href="/editor/media/"+route_id+"/";
	}
	
	if(newMedia.length>media.lenght) {
		
		alert(newMedia.length);
		
		window.location.href="/editor/media/"+route_id+"/";
	}
}

// Opens the window with publish options
function openFileUpload(e){

    var $bg = $('.fadeBG');
    var $upload = $('.upload-file');
    var $btnAbort = $('.upload-abort');
    var $btn = $('.upload-btn');
    
    

    $btnAbort.on('click',function(){
        $bg.fadeOut();
        $upload.fadeOut();
    });
    $btn.on('click',function(){
        uploadSelectedFile(function(){
            $bg.fadeOut();
            $upload.fadeOut();
        });

    })
    
   
    var top = ($(window).height()/2) - ($upload.outerHeight()/2);
    var left = ($(window).width()/2) - ($upload.outerWidth()/2);
    $upload.css({top:top,left:left});

    $bg.fadeIn();
    $upload.fadeIn();

}

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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function uploadSelectedFile(){
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    console.log("entered "+$( '#media_file' ).value);
    //console.log($( '#media_file' )[0].files[0]);
    console.log("entered1");

    var formData = new FormData();
    formData.append( 'file', $( '#media_file' )[0].files[0] );

    var request = $.ajax({
        url: "/upload/mediafile/",
        type: "POST",
        data: formData,
        xhr: function() {  // custom xhr
            myXhr = $.ajaxSettings.xhr();
            if(myXhr.upload){ // if upload property exists
                myXhr.upload.addEventListener('progress', progressHandlingFunction, false); // progressbar
            }
            return myXhr;
        },
        success: function(res){
            console.log("SUCCESS");
            newMedia = $('.media-opt');
            console.log(newMedia);
            console.log(newMedia.length);
            //console.log(res);
        }
    });
}



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
	
	//alert("Start publishing "+$("input[name='publish']").val());
	
	var markersMedia = $('.markersCheckboxes');
    
	 
	
    /*if(markersMedia.length!=0) {
    	console.log(markersMedia);
    	console.log(markersMedia[0].id);
    	console.log(markersMedia[0].checked);
    	
    }*/
    
    var markers = []
    
    for(var i=0;i<markersMedia.length;i++) {
    	
    	//console.log(markersMedia[i].checked);
    	var marker_id = {
    				
    				"id":markersMedia[i].id,
    				"checked":markersMedia[i].checked
    				
    		};
    		markers.push(marker_id);
    		
    }
    
    var markers_media={};
    
    markers_media['markers_media'] = markers;
    
    //console.log(JSON.stringify(markers_media));

	
   /* var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    var formData = new FormData();
    formData.append( 'file', $( '#media_file' )[0].files[0] ); */

  /*  var request = $.ajax({
        url: "/publish/trail/",
        type: "POST",
        data: "",
        xhr: function() {  // custom xhr
            myXhr = $.ajaxSettings.xhr();
            if(myXhr.upload){ // if upload property exists
                myXhr.upload.addEventListener('progress', progressHandlingFunction, false); // progressbar
            }
            return myXhr;
        },
        success: function(res){
            console.log("SUCCESS");
            //console.log(res);
        }
    });*/ 
	
	var request = $.ajax({
		url: "/editor/publish/"+$("input[name='publish']").val()+"/",
        type: "POST",
        dataType:"json",
        data: JSON.stringify(markers_media),
        contentType: "application/json;charset=utf-8",
       
        success: function(res){
            console.log("SUCCESS");
            
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

function publishTrail() {
	
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
		url: "/editor/publish/"+$("input[name='publish']").val()+"/",
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

function createMediaOptionsWindow(e){

    $('body').find('.media-info-box').each(function() {
        $(this).remove();
    });
    $('body').find('.fadeBG').each(function() {
        $(this).remove();
    });

    var $mediabox = $('<div>',{class:"media-info-box"});
    var $topbar = $('<div>',{class:"top-bar"});
    var $btnAbort = $('<button>',{class:"btn",text:"Avbryt"});
    var $header = $('<div>',{class:"header-text"});
    var $p = $('<p>',{class:"small-text",text:"namnpåfil.jpg"});
    var $btnFinished = $('<button>',{class:"btn right",text:"Klar"});
    var $optionsMenu = $('<div>',{class:"options-menu"});
    var $option1 = $('<div>',{class:"option"});
    var $option2 = $('<div>',{class:"option"});
    var $option3 = $('<div>',{class:"option"});
    var $label1 = $('<label>',{class:"small-text",text:"Panorama"});
    var $radio1 = $('<input>',{type:"radio",name:"options",value:"panorama",checked:false});
    var $label2;
    var $radio2;
    
    console.log("elements in media "+media.length);
    
    var elements = $('.media-opt');
    
    if(e.val()=="1")
      $radio1.prop("checked",true);
     
     
    
    if((elements.length==1) &&(e.attr('name') == $('.media-opt')[0].name)) {
    
    	$label2 = $('<label>',{class:"small-text",text:"Visas med kamerabild i bakgrunden"});
        $radio2 = $('<input>',{type:"radio",name:"options",value:"camera_bg",checked:false});
    }
    else {
    	
    	var $label2 = $('<label>',{class:"small-text",text:"Visas med kamerabild i bakgrunden",style:"color:#aaa"});
        var $radio2 = $('<input>',{type:"radio",name:"options",value:"camera_bg",disabled:'disabled',checked:false});
    }
    
    if(e.val()=="2")
    	$radio2.prop("checked",true);
    
    //var $label2 = $('<label>',{class:"small-text",text:"Visas med kamerabild i bakgrunden"});
    //var $radio2 = $('<input>',{type:"radio",name:"options",value:"camera_bg"});
    var $label3 = $('<label>',{class:"small-text",text:"Visas i helskärm"});
    var $radio3 = $('<input>',{type:"radio",name:"options",value:"fullscreen",checked:false});
    
    if(e.val()=="3")
    	$radio3.prop("checked",true);

    var $bg = $('<div>',{class:"fadeBG"});

    $btnAbort.on('click',function(){
        $mediabox.remove();
        $bg.remove();
    })
    
  /*  if(e.attr('name') == $('.media-opt')[0].name) {
    	
    	
        $option2.disabled = false;
 
    }
    else {
    	console.log($radio2);
    	alert($radio2.name);
    	$("input[value='camera_bg']").prop('disabled',true);
    	$option2.disabled = true;
    	$radio2.disabled = true;
    } */
    
    $btnFinished.on('click',function(){
    	
    	$mediabox.remove();
	    $bg.remove();
	    
	    if(($radio1).prop("checked") == true)
	    	type=1;
	    if(($radio2).prop("checked") == true)
	    	type=2;
	    if(($radio3).prop("checked") == true)
	    	type=3;
	    	
    	addImageType(e,e.attr('name'),type);
    	
    })

    $header.append($p);
    $topbar.append($btnAbort);
    $topbar.append($header);
    $topbar.append($btnFinished);
    $mediabox.append($topbar);
    $option1.append($label1);
    $option1.append($radio1);
    $option2.append($label2);
    $option2.append($radio2);
    $option3.append($label3);
    $option3.append($radio3);
    $optionsMenu.append($option1)
    $optionsMenu.append($option2)
    $optionsMenu.append($option3)
    $mediabox.append($optionsMenu);
    
    var nodes = $option2;
    
    $radio2.disabled = true;

    $bg.appendTo('body').hide().fadeIn(1000);
    $mediabox.appendTo('body');

    var marginLeft = 48
    var marginTop = -6
    $mediabox.css({left: e.offset().left+marginLeft+"px" , top: e.offset().top + marginTop + "px"});
    
    
}

function addImageType(e,button_id,type){
	
	var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                alert(csrftoken);
            }
        }
    });
    
    var route_id = $('.startmedia-wrapper').attr("id");
    var marker_id = $('.media-files').attr("id");
    
	
	var request = $.ajax({
        url: "/editor/media/marker/"+route_id+"/"+marker_id+"?id="+button_id+"&type="+type,
        type: "GET",
        //data: "id="+$('.media-opt').attr("name")+"&type="+type,
        xhr: function() {  // custom xhr
            myXhr = $.ajaxSettings.xhr();
            return myXhr;
        },
        success: function(res){
            console.log("SUCCESS entered");
            //console.log(res['imageType']);
            //alert("Hi");
            //console.log("Hi");
            console.log(res);
            $('.add-media').attr("name",res);
            e.val(res);
        }
    });
}
