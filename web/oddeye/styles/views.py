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
    style_dir='static/star/removed_bg/'
    stars=os.listdir(style_dir)
    imgs=[]
    for j in range(1, 4):
        for i in stars:
            imgs.append(style_dir+i+'/'+str(j)+'.png')

    # stars = ['iu', 'irene', 'hyuna', 'yerin', 'sunmi', 'jennie']
    thumbnails = os.listdir('static/step1/star_thumbnails')

#    context = {"stars": stars, "thumbnails": [thumbnails[:4],thumbnails[4:8],thumbnails[8:]], "thumb_range": range(4, len(thumbnails), 4)}
    context = {"stars": imgs, "thumbnails": thumbnails}

    return render(req, 'styles/main.html', context)

def StylesList(req):
    sql = '''
    SELECT NAME, STYLE, LIKEY
    FROM 
    (
        SELECT NAME, STYLE, LIKEY, ROW_NUMBER() OVER(PARTITION BY NAME ORDER BY LIKEY DESC) as rn
        FROM STAR
    )
    WHERE rn <= 1
    '''

    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()
    cursor.execute(sql)
    db_data = dictfetchall(cursor)
    # print(db_data)

    SQL = '''
        SELECT TAG
        FROM STAR
    '''
    cursor.execute(SQL)
    result = cursor.fetchall()
    tags = []

    for r in result:
        tags.append(r[0])

    tags = set(tags)
    # print(tags)

    page = req.GET.get('page',1)

    p = Paginator(db_data, 6)
    sub = p.page(page)

    context = {'stars':sub, 'tags':tags, "page":page}
    # print(context)

    return render(req, 'styles/list.html', context)

class StarView(View):
    def get(self, req, star_name):
        star_name=star_name
        sql = "SELECT style, likey, tag FROM Star WHERE name = '{}' ORDER BY likey".format(star_name)
        conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        cursor = conn.cursor()
        cursor.execute(sql)
        db_data = dictfetchall(cursor)
        print(db_data)

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
        context = {"star_name":star_name, 'styles': db_data, "products": product_info * 20}

        return render(req, 'styles/detail.html', context)

    def post(self, req):
        starpk = req.POST.get('starpk', None)
        star = get_object_or_404(Star, starpk=starpk)
        star_like, star_like_created = star.like_set.get_or_create(user=request.user)

        if not star_like_created:
            star_like.delete()
            message = "좋아요 취소"
        else:
            message = "좋아요"
        context = {'like_count': star.like_count,
                   'message' : message,
                   'nickname': request.uesr.profile.nickname}
        return HttpResponse(json.dumps(context), context_type="application/json")   #context를 json type으로
