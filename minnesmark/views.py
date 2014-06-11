# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

import datetime


#def current_datetime(request):
#    now = datetime.datetime.now()
#    return render(request, 'test/current_datetime.html', {'current_date': now})

def username_validation(username):
    """Check validation for username"""
    errors = []
    #Check if Username exists
    if(username_present(username)):
        errors.append("Anv��ndarnamnet finns redan.")
    #Username needs to be longer then 3 chars
    if(len(username) <= 3):
        errors.append("Anv��ndarnamnet m��ste vara 3 tecken eller l��ngre.")

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
        errors.append("L��senorden matchade inte.")
    if(len(pass1) < 3):
        errors.append("L��senordet m��ste vara l��ngre ��n 3 bokst��ver.")
    
    return errors

def register_account(request):
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
            #return HttpResponseRedirect("/editor/general")
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

