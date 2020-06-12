from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse,JsonResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import cx_Oracle
# from django.db import connection # DB에서 데이터를 받아오기 위한 라이브러리
# from styles.models import star # DB에서 필요한 table import

import os

# Create your views here.
# sql 날려서 받아온 결과를 dict 형태로 만들어주는 함수
def dictfetchall(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

def main(req):
    stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    thumbnails = os.listdir('static/step1/star_thumbnails')

#    context = {"stars": stars, "thumbnails": [thumbnails[:4],thumbnails[4:8],thumbnails[8:]], "thumb_range": range(4, len(thumbnails), 4)}
    context = {"stars": stars, "thumbnails": thumbnails}

    return render(req, 'styles/main.html', context)

def main2(req):
    return render(req, 'styles/main2.html')

def StylesList(req):

    # DB 연동 후 사용할 코드
    sql = """
        SELECT NO, NAME, LIKE FROM STAR;
    """
    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()
    cursor.execute(sql)
    temp_result = dictfetchall(cursor)

    print(temp_result)



    # # 임시 코드
    # result = [{'no': 37, 'name': 'dahee', 'style': 1, 'like': 100},
    #           {'no': 45, 'name': 'hani', 'style': 1, 'like': 100},
    #           {'no': 19, 'name': 'hyuna', 'style': 1, 'like': 84},
    #           {'no': 10, 'name': 'irene', 'style': 1, 'like': 88},
    #           {'no': 1, 'name': 'iu', 'style': 1, 'like': 65},
    #           {'no': 17, 'name': 'jennie', 'style': 1, 'like': 80},
    #           {'no': 34, 'name': 'sunmi', 'style': 1, 'like': 99},
    #           {'no': 25, 'name': 'yerin', 'style': 1, 'like': 98},
    #           {'no': 8, 'name': 'seulgi', 'style': 1, 'like': 79}]
    #

    context = {'stars':result}

    # stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']



    # return render(req, 'styles/list.html',{'stars' : stars} )
    return render(req, 'styles/list.html', context)

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
        context = {"star": star, "products": product_info * 20}
        return render(req, 'styles/detail.html',context=context)
    
   
def test(req):
    stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    thumbnails = os.listdir('static/step1/star_thumbnails')

    context = {"stars": [stars[:3],stars[3:]], "thumbnails": thumbnails, "thumb_range": range(4, len(thumbnails), 4)}

    return render(req, 'styles/test.html', context)

def redirect(req):
    
    return redirect(req)