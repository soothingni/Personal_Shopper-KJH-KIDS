from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User

import os

# Create your views here.
def main(req):
    stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    thumbnails = os.listdir('static/step1/star_thumbnails')

    context = {"stars": stars, "thumbnails": [thumbnails[:4],thumbnails[4:8],thumbnails[8:]], "thumb_range": range(4, len(thumbnails), 4)}

    return render(req, 'styles/main.html', context)

def main2(req):
    return render(req, 'styles/main2.html')

def StylesList(req):
    stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']

    return render(req, 'styles/list.html',{'stars' : stars} )

def StyleDetail(req):
    star = '아이유'
    
    product_info = [
        {"product_url": "https://www.seoulstore.com/products/955954/detail", "img_url": "https://images.seoulstore.com/products/52a6ed2a1d61b21e79e0f3a5c1f03263.jpg?d=640xauto", "sub_category": 0, "category": 0, "super_category": 0, "key": "955954"}, 
        {"product_url": "https://www.seoulstore.com/products/1178222/detail", "img_url": "https://images.seoulstore.com/products/c04a10c862fed49321b275886ff91596.jpg?d=640xauto", "sub_category": 0, "category": 0, "super_category": 0, "key": "1178222"}, 
        {"product_url": "https://www.seoulstore.com/products/1176995/detail", "img_url": "https://images.seoulstore.com/products/0405007e66dcf5326511bfac12df5750.jpg?d=640xauto", "sub_category": 0, "category": 0, "super_category": 0, "key": "1176995"}
    ]
    context = {"star": star, "products": product_info}    #띄울 상품
    return render(req, 'styles/detail.html', context )

class StarView(View):
    def get(self, req, star_name):
        star=star_name
        # stars = {'iu':'iu', 'irene':'irene', 'hyuna':'hyuna', 'yerin':'yerin', 'sunmi':'sunmi', 'jennie':'jennie'}
        # star = starts[star]
        # thumbnails = os.listdir('static/step1/{}_thumbnails'.format('stars'))

        product_info = [
            {"product_url": "https://www.seoulstore.com/products/955954/detail",
             "img_url": "https://images.seoulstore.com/products/52a6ed2a1d61b21e79e0f3a5c1f03263.jpg?d=640xauto",
             "sub_category": 0, "category": 0, "super_category": 0, "key": "955954"},
            {"product_url": "https://www.seoulstore.com/products/1178222/detail",
             "img_url": "https://images.seoulstore.com/products/c04a10c862fed49321b275886ff91596.jpg?d=640xauto",
             "sub_category": 0, "category": 0, "super_category": 0, "key": "1178222"},
            {"product_url": "https://www.seoulstore.com/products/1176995/detail",
             "img_url": "https://images.seoulstore.com/products/0405007e66dcf5326511bfac12df5750.jpg?d=640xauto",
             "sub_category": 0, "category": 0, "super_category": 0, "key": "1176995"}
        ]
        context = {"star": star, "products": product_info}
        return render(req, 'styles/detail.html',context=context)


def test(req):
    stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    thumbnails = os.listdir('static/step1/star_thumbnails')

    context = {"stars": [stars[:3],stars[3:]], "thumbnails": thumbnails, "thumb_range": range(4, len(thumbnails), 4)}

    return render(req, 'styles/test.html', context)

def redirect(req):
    
    return redirect(req)