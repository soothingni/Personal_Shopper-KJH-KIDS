from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from django.views.generic.edit import FormView
from django.contrib.auth.hashers import make_password, check_password


# db
import cx_Oracle


from .models import OddeyeUsers
from .forms import RegisterForm, LoginForm


# 사용할 모듈
import math
import os
import json
import random
import numpy as np

def dictfetchall(cursor):
    desc = cursor.description
    return [ dict( zip([col[0] for col in desc], row) ) for row in cursor.fetchall()]

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

        user = auth.authenticate(
            username=username,
            password=password
        )

        print(username, '------>LOGIN')

        if user is not None:
            auth.login(self.request, user)

        return super().form_valid(form)


def logout(req):
    auth.logout(req)
    return redirect('main')


def aboutus(req):
    return render(req, 'styles/aboutus.html')

def myaccounts(req):

    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()
    # Product Data 가져오기
    sql = '''
            SELECT product_ID, img_url, product_url, product_name, price_original, price_discount
            FROM Products
            '''
    cursor.execute(sql)
    prod_data = dictfetchall(cursor)

    # User Info 가져오기
    sql = '''
            SELECT NO, USERNAME, FOLLOWING, WISH_LIST
            FROM ODDEYE_USERS
            '''
    cursor.execute(sql)
    user_data = dictfetchall(cursor)
    user_id=req.session['username']
    for user in user_data:
        if user['USERNAME'] == user_id:
            selected_user = user
    user_following = list(selected_user['FOLLOWING'].split(','))
    user_wishlist = list(selected_user['WISH_LIST'].split(','))
    user_prod = []
    for prod in prod_data:
        if str(prod['PRODUCT_ID']) in user_wishlist:
            if prod['PRICE_DISCOUNT']:
                prod['discounts'] = int((prod['PRICE_ORIGINAL'] - prod["PRICE_DISCOUNT"]) / prod['PRICE_ORIGINAL'] * 100)
                prod['PRICE_DISCOUNT']=format(prod['PRICE_DISCOUNT'], ",")
            prod["PRICE_ORIGINAL"]=format(prod['PRICE_ORIGINAL'], ",")
            user_prod.append(prod)


    context={"data" : user_prod, "follow" : user_following, 'username':user_id}

    return render(req, 'accounts/myaccounts.html', context=context)

def dictfetchall(cursor):
    desc = cursor.description
    return [ dict( zip([col[0] for col in desc], row) ) for row in cursor.fetchall()]
