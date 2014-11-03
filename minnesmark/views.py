# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail


import datetime
import json


#def current_datetime(request):
#    now = datetime.datetime.now()
#    return render(request, 'test/current_datetime.html', {'current_date': now})

def username_validation(username):
    """Check validation for username"""
    errors = []
    #Check if Username exists
    if(username_present(username)):
        errors.append("Användarnamnet finns redan.")
    #Username needs to be longer then 3 chars
    if(len(username) <= 3):
        errors.append("Användarnamnet mäste vara 3 tecken eller längre.")

    return errors

def username_present(username):
    """Check Database for username, return true if found"""
    if User.objects.filter(username=username).count():
        return True
    return False

def password_validation(pass1,pass2):
    """Check validation for password"""
    errors = []
    if(pass1 != pass2):
        errors.append("Lösenorden matchade inte.")
    if(len(pass1) < 3):
        errors.append("Lösenordet måste vara längre än 3 bokstöver.")
    
    return errors

def register_account(request):
    
    if request.is_ajax():
        if(request.method=="POST"):
            response_data = {}
            print(request.user.id)
            try:
                all_errors = []
                json_str = request.body.decode(encoding='UTF-8')
                json_obj = json.loads(json_str)
                userdata = json_obj['data']
                data = userdata[0]
                print(userdata)
                
                print(data['username'])
                print("str "+str(len(data['username'])))
                print("str1 " +str(len(data['email'])))
                
                user = User.objects.get(id=int(request.POST['userid']))
                
                if(len(data['username']) != 0 ):
                    all_errors.extend(username_validation(data['username']))
                    
                if(len(data['password'])!=0):
                    all_errors.extend(password_validation(data['password'],user.password))
                    
                if(len(all_errors) != 0):
                    response_data["errors"] = all_errors
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                
                #print(data.username)
                print("length " +str(len(userdata)))
            except:
                response_data['emptyData'] = "No data"
                
        
        response_data["user_id"] = request.user.id
        return HttpResponse(json.dumps(response_data), content_type="application/json")
        
    
    if request.method == "POST":
        #array for all error to be displayed if validation fails.
        all_errors = []
        
        #Password Validation
        all_errors.extend(password_validation(request.POST['password'],request.POST['password_again']))
        #Username Validation
        all_errors.extend(username_validation(request.POST['username']))

        if(len(all_errors) <= 0):
            #Create new User
            newuser = User.objects.create_user(request.POST["username"],request.POST["email"], request.POST["password"])
            #Set Flag is_active to false
            newuser.is_active = False
            newuser.first_name = request.POST['firstname']
            newuser.last_name = request.POST['lastname']
                      
            #Save to database
            newuser.save()
            
            print(newuser.id)
            
            try:
                #send email to user for activation
                email = request.POST["email"]
                email_subject = 'Your new example.com account confirmation'
                email_body = "Hello, %s, and thanks for signing up for an Minnesmark.com account!\n\nTo activate your account, click this link within 48 hours:\n\nhttp://127.0.0.1:8000/accounts/confirm/%s" % (newuser.username,newuser.id) 
                send_mail(email_subject,email_body,'admin@minnesmark.com',[email])
            except:
                print("Could not send mail")
  
            return render(request,'registration/registration_complete.html')
        else:
            #Return view with all errors
            return render(request,'registration/registration_form.html',{'all_errors':all_errors})

    return render(request,'registration/registration_form.html')

@staff_member_required
def approveUser(request):
    if request.method == 'POST':
        user = User.objects.get(id=int(request.POST['userid']))
        user.is_active = True
        user.save()
    
        users = User.objects.filter(is_active=False)
        return render(request,'admin/approve.html',{"users":users})
    
    users = User.objects.filter(is_active=False)
    return render(request,'admin/approve.html',{"users":users})

def confirmUser(request,userid):
    
    user = User.objects.get(id=int(userid))
    user.is_active = True
    user.save()
    
    users = User.objects.filter(id=int(userid),is_active=True)
    return render(request,'admin/approve.html',{"users":users})
    
def getUserData(request):
    
    if request.is_ajax():
        response_data = {}
        print(request.user.id)
        user = User.objects.get(id=int(request.user.id))
        response_data['username'] = user.username
        response_data['firstname'] = user.first_name
        response_data['lastname'] = user.last_name
        response_data['email'] = user.email
        return HttpResponse(json.dumps(response_data), content_type="application/json")
        

    

