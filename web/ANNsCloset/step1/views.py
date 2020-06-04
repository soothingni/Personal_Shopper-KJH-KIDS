from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
import os

# Create your views here.
def home(req):
    return render(req, 'step1/home.html')

def main(req):
    stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    thumbnails = os.listdir('static/step1/star_thumbnails')
    
    context = {"stars": stars, "thumbnails": thumbnails, "thumb_range": range(4, len(thumbnails), 4)}
    return render(req, 'step1/main.html', context)

def aboutus(req):
    return render(req, 'step1/aboutus.html')

def stars(req):
    return render(req, 'step1/stars.html')


def StarsView(req):
    return render(req, 'step1/stars.html')

def goods(req):
    return render(req, 'step1/goods.html')