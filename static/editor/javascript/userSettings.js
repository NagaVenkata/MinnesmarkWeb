$('document').ready(function(){
    /*
        Get Active and display menu on load
     */
	
	$("#userProfile").on('click',function() {
		
		getUserProfile();
		//showUserProfile(this);
	});
	
	
	
	
});

//gets the user profile
function getUserProfile() {
	
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
    
    
	var request = $.ajax({
        url: "/accounts/getuser",
        type: "GET",
        //data: "id="+$('.media-opt').attr("name")+"&type="+type,
        xhr: function() {  // custom xhr
            myXhr = $.ajaxSettings.xhr();
            return myXhr;
        },
        success: function(res){
            console.log("SUCCESS entered");
            console.log(res);
            showUserProfile(res);
        }
    });
}

function showUserProfile(data){
	
	console.log(data.email);
	
	var userProfile = document.createElement("div");
	
	//userProfile.setAttribute('method',"post");
	//userProfile.setAttribute('action',"/accounts/register");

	var userfieldset = document.createElement("fieldset");
	var username = document.createElement("input"); //input element, text
	username.setAttribute('type',"text");
	username.setAttribute('name',"username");
	username.setAttribute('placeholder',data.username);
	username.setAttribute("id","username");
	
	var usernameLabel = document.createElement("label");
	usernameLabel.setAttribute("for","username");
	usernameLabel.innerHTML = "Användarnamn:";
	
	var emailfieldset = document.createElement("fieldset");
	var email = document.createElement("input"); //input element, text
	email.setAttribute('type',"text");
	email.setAttribute('name',"email");
	email.setAttribute('placeholder',data.email);
	email.setAttribute("id","email");
	
	var emailLabel = document.createElement("label");
	emailLabel.setAttribute("for","email");
	emailLabel.innerHTML = "Epost:";
	
	
	var firstnamefieldset = document.createElement("fieldset");
	var firstname = document.createElement("input"); //input element, text
	firstname.setAttribute('type',"text");
	firstname.setAttribute('name',"firstname");
	firstname.setAttribute('placeholder',data.firstname);
	firstname.setAttribute("id","firstname");
	
	var firstnameLabel = document.createElement("label");
	firstnameLabel.setAttribute("for","firstname");
	firstnameLabel.innerHTML = "Förnamn:";
	
	
	var lastnamefieldset = document.createElement("fieldset");
	var lastname = document.createElement("input"); //input element, text
	lastname.setAttribute('type',"text");
	lastname.setAttribute('name',"lastname");
	lastname.setAttribute('placeholder',data.lastname);
	lastname.setAttribute("id","lastname");
	
	var lastnameLabel = document.createElement("label");
	lastnameLabel.setAttribute("for","lastname");
	lastnameLabel.innerHTML = "Efternamn:";
	
	
	var passwordfieldset = document.createElement("fieldset");
	var password = document.createElement("input"); //input element, text
	password.setAttribute('type',"text");
	password.setAttribute('name',"password");
	password.setAttribute('placeholder',"Losenord...");
	password.setAttribute("id","password");
	
	var passwordLabel = document.createElement("label");
	passwordLabel.setAttribute("for","password");
	passwordLabel.innerHTML = "Losenord:";
	

	var submit = document.createElement("input"); //input element, Submit button
	submit.setAttribute('type',"button");
	submit.setAttribute('value',"Spara");
	submit.setAttribute("id","save");

	userfieldset.appendChild(usernameLabel);
	userfieldset.appendChild(username);
	userProfile.appendChild(userfieldset);
	
	emailfieldset.appendChild(emailLabel);
	emailfieldset.appendChild(email);
	userProfile.appendChild(emailfieldset);
	
	firstnamefieldset.appendChild(firstnameLabel);
	firstnamefieldset.appendChild(firstname);
	userProfile.appendChild(firstnamefieldset);
	
	lastnamefieldset.appendChild(lastnameLabel);
	lastnamefieldset.appendChild(lastname);
	userProfile.appendChild(lastnamefieldset);
	
	passwordfieldset.appendChild(passwordLabel);
	passwordfieldset.appendChild(password);
	userProfile.appendChild(passwordfieldset);
	
	//var csrftoken = getCookie('csrftoken');
	
	//userProfile.append(csrftoken);
	
	userProfile.appendChild(submit);
	
	
	$('body').find('#media-box').each(function() {
        $(this).remove();
    });
    $('body').find('.fadeBG').each(function() {
        $(this).remove();
    });
	
	
	var $mediabox = $('<div>',{id:'media-box'});
	//var $btnAbort = $('<button>',{class:"btn",text:"Avbryt"});
	
	
	var btnAbort = document.createElement("input"); //input element,button
	btnAbort.setAttribute('type',"button");
	btnAbort.setAttribute('id',"btnclose");
	btnAbort.setAttribute('value',"Avbryt");
	
	userProfile.appendChild(btnAbort);
	
	
	$mediabox.append(userProfile);
	
	$mediabox.appendTo('body');
	
	var marginLeft = 48
    var marginTop = -6
    $mediabox.css({left: marginLeft+"px" , top: marginTop + "px",position: 'fixed',
    top: 100+"px",
    left: 200+"px",
    width:380+"px",
    height: 200+"px",
    border: 2+"px"});
	
	$mediabox.css('border-color','#d6d5d2');
	
	$mediabox.css('background-color','#f7f6f3');
	
	$("#btnclose").on('click',function() {
		
		$mediabox.fadeOut();
		
	});
	
	$("#save").on('click',function(){
		
		saveProfile();
		
	});

	//and some more input elements here
	//and dont forget to add a submit button

	//document.getElementsByTagName('body')[0].appendChild(f);
	
	/*$('body').find('.media-info-box').each(function() {
        $(this).remove();
    });
    $('body').find('.fadeBG').each(function() {
        $(this).remove();
    });*/

    /*var $mediabox = $('<div>',{class:"media-info-box"});
    var $topbar = $('<div>',{class:"top-bar"});
    var $btnAbort = $('<button>',{class:"btn",text:"Avbryt"});
    var $header = $('<div>',{class:"header-text"});
    var $profileform = $('<form>',{id:"userprofile",method:"post",action:"accounts/register",id:"userprofile"});
    var $p = $('<p>',{class:"small-text",text:"text"});
    var $btnFinished = $('<button>',{class:"btn right",text:"Klar"});
    var $optionsMenu = $('<div>',{class:"options-menu"});
    var $submit = $('<input>',{type:"submit",value:"Submit"});
    
    
    
    var $username = $('<fieldset>',{class:"tag"});
    var $email = $('<fieldset>',{class:"tag"});
    var $firstname = $('<fieldset>',{class:"tag"});
    var $lastname = $('<fieldset>',{class:"tag"});
    var $password = $('<fieldset>',{class:"tag"});
    
   

    //var $option2 = $('<div>',{class:"option"});
    //var $option3 = $('<div>',{class:"option"});
    var $userInput =$('<input>', {id:"username", type:"text", name:"username", placeholder:"Användarnamn...", required:"required", id:"username"}); 
    var $userLabel = $('<label>',{for:"username",text:"Användarnamn:"});
    
    var $emailInput =$('<input>', {id:"email", type:"text", name:"email", placeholder:"Epost...", required:"required", id:"email"}); 
    var $emailLabel = $('<label>',{for:"email",text:"Epost:"});
    
    var $firstnameInput =$('<input>', {id:"firstname", type:"text", name:"firstname", placeholder:"Förnamm...", required:"required", id:"firstname"}); 
    var $firstnameLabel = $('<label>',{for:"firstname",text:"Förnamn:"});
    
    var $lastnameInput =$('<input>', {id:"lastname", type:"text", name:"lastname", placeholder:"Efternamn...", required:"required", id:"lastname"}); 
    var $lastnameLabel = $('<label>',{for:"lastname",text:"Efternamn:"});
    
    var $passwordInput =$('<input>', {id:"password", type:"password", name:"password", placeholder:"Lösenord", required:"required", id:"password"}); 
    var $passwordLabel = $('<label>',{for:"password",text:"Lösenord:"});
    
    
    $header.append($p);
    $topbar.append($btnAbort);
    $topbar.append($header);
    $topbar.append($btnFinished);
    $mediabox.append($topbar);*/
    
    
    
   /*$username.append($userLabel);
    $username.append($userInput);
    $optionsMenu.append($username);
    
    $email.append($emailLabel);
    $email.append($emailInput);
    $optionsMenu.append($email);

    
    $firstname.append($firstnameLabel);
    $firstname.append($firstnameInput);
    $optionsMenu.append($firstname);
    
    $lastname.append($lastnameLabel);
    $lastname.append($lastnameInput);
    $optionsMenu.append($lastname);
    
    $password.append($passwordLabel);
    $password.append($passwordInput);
    $optionsMenu.append($password);
    
    $optionsMenu.append($submit);*/
    
    //$optionsMenu.append(userProfile);
       
    
    //$mediabox.append($optionsMenu);
    
    
    
    
    /*$( "#userprofile" ).submit(function( event ) {
    	  alert( "Handler for .submit() called." );
    	  //event.preventDefault();
    	});*/
    
    
    
    //$bg.appendTo('body').hide().fadeIn(1000);
    /*$mediabox.appendTo('body');

    var marginLeft = 48
    var marginTop = -6
    $mediabox.css({left: e.offset().left+marginLeft+"px" , top: e.offset().top + marginTop + "px"});*/
	
}

function saveProfile() {
	
	var userData = {};
	
	var data = [];
	
	userdata = {
			
			"username":$("#username").val(),
	        "email":$("#email").val(),
			"firstname":$("#firstname").val(),
			"lastname":$("#lastname").val(),
			"password":$("#lastname").val()
	};
	
	data.push(userdata);
	
	/*if($("#username").val()) 
		data["username"]= $("#username").val(); 
	else 
		data["username"]= "";
	
	if($("#email").val())
		data["email"]= $("#email").val();
	else
		data["email"]= "";
	
	if($("#firstname").val())
		data["firstname"]=$("#firstname").val();
	else
		data["firstname"] = "";
	
	if($("#lastname").val())
		data["lastname"] = $("#lastname").val();
	else
		data["lastname"] = "";
	
	if($("#password").val())
		data["password"] = $("#password").val();
	else
		data["password"] = "";*/
	
	//userData.push(data);
	
	userData["data"] = data;
	
	console.log(userData);
	
	console.log(JSON.stringify(userData));
	
	//alert(userData.length);
	
	/*if(userData.length!=0)*/ //{
	
		var csrftoken = getCookie('csrftoken');
		$.ajaxSetup({
			crossDomain: false, // obviates need for sameOrigin test
			beforeSend: function(xhr, settings) {
				if (!csrfSafeMethod(settings.type)) {
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
					//alert(csrftoken);
				}
			}
		});
    
    
		var request = $.ajax({
			url: "/accounts/register",
			type: "POST",
			data: JSON.stringify(userData),
			contentType: "application/json;charset=utf-8",
			xhr: function() {  // custom xhr
				myXhr = $.ajaxSettings.xhr();
				return myXhr;
			},
			success: function(res){
				console.log("SUCCESS entered");
				console.log(res);
            
			}
		});
	//}
	/*else {
		
		alert("No settings have been changed");
	}*/
}
