from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import redirect
# Create your views here.
def home(req):
    return redirect('main')

def login(req):
    if req.method=="POST":
        username=req.POST['username']
        password=req.POST['password']
        user= auth.authenticate(req, username=username, password=password)
        if user is not None:
            auth.login(req, user)
            return redirect('main')
        else:
            return render(req, 'accounts/login.html', {'error': '아이디나 비밀번호가 일치하지 않습니다'})
    else:
        return render(req, 'accounts/login.html')

    return render(req, 'accounts/login.html')

def logout(req):
    auth.logout(req)
    return redirect('main')

def signup(req):
    if req.method=='POST':
        if req.POST['password1']==req.POST['password2']:
            user=User.objects.create_user(
                email=req.POST['email'],
                username=req.POST['username'],
                password=req.POST['password1']
            )
            auth.login(req, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main')
        return render(req, 'accounts/signup.html',{'error': '비밀번호가 일치하지 않습니다'})

    return render(req, 'accounts/signup.html')

def aboutus(req):
    return render(req, 'styles/aboutus.html')