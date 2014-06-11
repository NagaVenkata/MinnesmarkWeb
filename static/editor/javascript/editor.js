/**
 * Created by ante on 2014-03-27.
 */
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

    $('.media-opt').on('click',function(){
        createMediaOptionsWindow($(this));
    });

    //function is called when clicked on add media button
    $('.add-media').on('click',function(){
       openFileUpload($(this));
    });
    
    //function called when clicked on publish a trial
    $("input[name='publish']").on('click',function(){
    	
    	publishJsonFile($(this));
    	$("input[name='publish']").prop('disabled',true);	
     });
});

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
        publishSelectedTrail(function(){
            $bg.fadeOut();
            $upload.fadeOut();
        });

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
            //console.log(res);
        }
    });
}

function publishSelectedTrail(){
	
	alert("Start publishing "+$("input[name='publish']").val());
	
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
        type: "GET",
        success: function(res){
            console.log("SUCCESS");
            alert("Hi");
            //console.log(res);
        }
    }); 
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
    var $radio1 = $('<input>',{type:"radio",name:"options",value:"panorama"});
    var $label2 = $('<label>',{class:"small-text",text:"Visas med kamerabild i bakgrunden"});
    var $radio2 = $('<input>',{type:"radio",name:"options",value:"camera_bg"});
    var $label3 = $('<label>',{class:"small-text",text:"Visas i helskärm"});
    var $radio3 = $('<input>',{type:"radio",name:"options",value:"fullscreen"});

    var $bg = $('<div>',{class:"fadeBG"});

    $btnAbort.on('click',function(){
        $mediabox.remove();
        $bg.remove();
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

    $bg.appendTo('body').hide().fadeIn(1000);
    $mediabox.appendTo('body');

    var marginLeft = 48
    var marginTop = -6
    $mediabox.css({left: e.offset().left+marginLeft+"px" , top: e.offset().top + marginTop + "px"});
}