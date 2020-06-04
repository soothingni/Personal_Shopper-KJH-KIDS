from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import redirect
# Create your views here.
def home(req):
    return render(req, 'home.html')

def login(req):
    if req.method=="POST":
        username=req.POST['username']
        password=req.POST['password']
        user= auth.authenticate(req, username=username, password=password)
        if user is not None:
            auth.login(req, user)
            return redirect('home')
        else:
            return render(req, 'login.html', {'error': 'username or password is incorrect'})
    else:
        return render(req, 'login.html')

    return render(req, 'login.html')

def logout(req):
    auth.logout(req)
    return redirect('home')

def signup(req):
    if req.method=='POST':
        if req.POST['password1']==req.POST['password2']:
            user=User.objects.create_user(
                username=req.POST['username'],
                password=req.POST['password1']
            )
            auth.login(req, user)
            return redirect('home')
        return render(req, 'signup.html')

    return render(req, 'signup.html')

