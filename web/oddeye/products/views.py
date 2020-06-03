from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import os

# Create your views here.
def ProductsList(req):
    # stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    # thumbnails = os.listdir('static/step1/star_thumbnails')
    #
    # context = {"stars": stars, "thumbnails": thumbnails, "thumb_range": range(4, len(thumbnails), 4)}
    return render(req, 'products/list.html')