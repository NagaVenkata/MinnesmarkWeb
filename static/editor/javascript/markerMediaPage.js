$('document').ready(function(){
    
   /* $('.close').on('click',function(){
        var route_id = "{{cur_route.id}}";   
    	window.open("/editor/media/"+route_id+"/","_self");
    }); */
	
	/*$('.marker-add-media').click(function(){
		
		openFileUpload(this);
	});*/
	
    /*$("#done").click(function(){
    	
    	alert("done clicked");
    	
    });*/

 
});

//Opens the window with publish options
/*function openFileUpload(e){

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

}*/