from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
# Create your views here.
from .models import OddeyeUsers
from .forms import RegisterForm, LoginForm
from django.views.generic.edit import FormView
from django.contrib.auth.hashers import make_password, check_password


def home(req):
    return redirect('main')

class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = "/"

    def form_valid(self, form):
        oddeye_user = OddeyeUsers(
            id = form.data.get('id'),
            password = make_password(form.data.get('password')),
        )
        oddeye_user.save()

        return super().form_valid(form)

class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = "/"

    # 세션 추가
    def form_valid(self, form):
        self.request.session['id'] = form.data.get('id')


        user = authenticate(
            id = form.data.get('id'),
            password = form.data.get('password')
        )
        # user = auth.authenticate(id=form.data.get('id'), password=form.data.get('password'))

        return super().form_valid(form)

def logout(req):
    auth.logout(req)
    return redirect('main')


def aboutus(req):
    return render(req, 'styles/aboutus.html')