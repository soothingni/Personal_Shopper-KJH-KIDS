from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import os
import json
import random
# Create your views here.
def ProductsList(req):
    with open("static/json/categorized_tong.json",'r') as json_file:
        seoul_json=json.load(json_file)


    # stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    # thumbnails = os.listdir('static/step1/star_thumbnails')
    #
    # context = {"stars": stars, "thumbnails": thumbnails, "thumb_range": range(4, len(thumbnails), 4)}
    return render(req, 'products/list.html')

def jsontest(req):
    with open("static/json/categorized_tong.json",'r') as json_file:
        seoul_json=json.load(json_file)


    send_list=[]
    for item in seoul_json:
        if item['sub_category']==random.randint(0,10):
            send_list.append(item)

    context = {"seoul_json": send_list}
    return render(req,'products/json_test.html', context=context )

def modaltest(req):
    return render(req, 'products/modaltest.html')