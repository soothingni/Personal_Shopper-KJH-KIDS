from django.shortcuts import render
import os

# Create your views here.
def main(req):
    stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    thumbnails = os.listdir('static/step1/star_thumbnails')

    context = {"stars": stars, "thumbnails": thumbnails, "thumb_range": range(4, len(thumbnails), 4)}

    return render(req, 'styles/main.html', context)

def main2(req):
    return render(req, 'styles/main2.html')


def StylesList(req):
    return render(req, 'styles/list.html')
