from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
# Create your views here.
from .models import OddeyeUsers
from .forms import RegisterForm, LoginForm
from django.views.generic.edit import FormView
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User

def home(req):
    return redirect('main')

class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = "/"

    def form_valid(self, form):
        oddeye_user = OddeyeUsers(
            username = form.data.get('username'),
            password = make_password(form.data.get('password')),
        )
        oddeye_user.save()

        # Create user and save to the database
        user_main = User.objects.create_user(form.data.get('username'), '', form.data.get('password'))
        user_main.save()

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = auth.authenticate(
            username=username,
            password=password
        )

        auth.login(self.request, user)

        return super().form_valid(form)

class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = "/"

    # 세션 추가
    def form_valid(self, form):
        self.request.session['username'] = form.data.get('username')

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        print(username)
        print(password)
        user = auth.authenticate(
            username=username,
            password=password
        )
        print(user)

        if user is not None:
            auth.login(self.request, user)

        return super().form_valid(form)


def logout(req):
    auth.logout(req)
    return redirect('main')


def aboutus(req):
    return render(req, 'styles/aboutus.html')