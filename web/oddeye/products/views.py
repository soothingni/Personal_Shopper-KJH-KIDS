from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import cx_Oracle
from accounts.models import OddeyeUsers
''' 여기는 django db (sqlite) 사용할 때 필요한 모듈?
from django.db import connection # DB에서 데이터를 받아오기 위한 라이브러리
from products.models import product # DB에서 필요한 table import
'''
import math
import os
import json
import random
import numpy as np
# Create your views here.


# DB에서 불러온 데이터를 field명(img_url, product_url)과 결합하기 위한 함수. 수업 내용 확인
def dictfetchall(cursor):
    desc = cursor.description
    return [ dict( zip([col[0] for col in desc], row) ) for row in cursor.fetchall()]

def productview(req):
    return redirect('products:prod_list','9')

class prod_list(View):
    def get(self, req, pk):
        global category_name
        global category_dict
        sql = '''
        SELECT super_category, base_category, sub_category, product_ID,img_url, product_url,product_name ,price_original,price_discount
        FROM Products
        '''
        conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        cursor = conn.cursor()
        cursor.execute(sql)
        db_data = dictfetchall(cursor)

        sql = '''
                SELECT STAR_EMBEDDING.STAR_EMBEDDING, STAR.NAME, STAR.STYLE, STAR.CATEGORY
                FROM STAR_EMBEDDING
                JOIN STAR ON STAR.NO=STAR_EMBEDDING.ID

                '''
        cursor.execute(sql)
        star_data = dictfetchall(cursor)






        for item in db_data:
            if item['PRICE_DISCOUNT'] != None:
                item['PRICE_DISCOUNT_COMMA'] = format(item['PRICE_DISCOUNT'], ",")
            item['PRICE_ORIGINAL_COMMA'] = format(item['PRICE_ORIGINAL'], ",")
        new_dict=[]
        if int(pk)==9:
            new_dict=db_data
        else:
            for dt in db_data:

                if dt['BASE_CATEGORY'] == int(pk):
                    new_dict.append(dt)
        random.shuffle(new_dict)
        paginator = Paginator(new_dict, 30)
        page = req.GET.get("page", 1)
        subs = paginator.get_page(page)
        page_range = 5

        current_block = math.ceil(int(page) / page_range)
        start_block = (current_block - 1) * page_range
        end_block = start_block + page_range
        p_range = paginator.page_range[start_block:end_block]

        context = {'data': subs, 'cat': category_name, 'p_range': p_range}

        return render(req, 'products/list.html', context)
    def post(self, req, pk):
#        prod_id = req.POST.get('pk', None)
        prod_id = pk

        current_user = req.session['username']
        myuser = OddeyeUsers.objects.get(username=current_user)
        mywi = myuser.wish_list
        mywi_set = set(mywi.split(','))
        if prod_id not in mywi_set:
            mywi_set.add(prod_id)
            print('add {}'.format(prod_id))
        # else:
        #     mywi_set.discard(prod_id)
        #     print('delete {}'.format(prod_id))

        mywi_set.discard('')  # 빈칸을 element로 갖는 경우가 있어서.
        mywi_set_str = str(mywi_set)
        if len(mywi_set) == 0: mywi_set_str = ''  # 빈칸을 set()으로 문자 그대로 넣어서.
        myuser.wish_list = mywi_set_str.replace('{', "").replace('}', "").replace("'", "").replace('"', "").replace(" ","").strip(',')
        myuser.save()

        # starpk = req.POST.get('starpk', None)
        # star = get_object_or_404(Star, starpk=starpk)
        # star_like, star_like_created = star.like_set.get_or_create(user=request.user)
        #
        context = {
                   # 'message':message,
                   }
        return JsonResponse(context)


def prod_embedding(req, pk):
    sql = '''
        SELECT PRODUCTS_EMBEDDING.id, PRODUCTS_EMBEDDING.product_embedding, PRODUCTS.img_url, PRODUCTS.product_url, PRODUCTS.SUPER_CATEGORY
        FROM PRODUCTS_EMBEDDING
        JOIN PRODUCTS ON PRODUCTS_EMBEDDING.ID = PRODUCTS.PRODUCT_ID
        '''
    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()
    cursor.execute(sql)
    db_data = dictfetchall(cursor)
    dist=[]

    sup_cat=db_data[pk]['SUPER_CATEGORY']

    for i in db_data:
        if i['SUPER_CATEGORY']==sup_cat:
            dist.append(
                {
                    'product_id':i['ID'],
                    'distance':compute_linalg_dist(np.array(list(map(float,(db_data[pk]['PRODUCT_EMBEDDING'][2:-2].split(','))))),
                                                   np.array(list(map(float,(i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                    'img_url':i['IMG_URL'],
                    'product_url':i['PRODUCT_URL']
                }
            )
    dist=sorted(dist, key=lambda x : (x['distance'], x['product_id']))

    if len(dist)>5:
        context = {"dist": dist[:5]}
    else:
        context={"dist":dist}

    return render(req, 'products/empty2.html', context)

def star_embedding(req, pk):

    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()

    sql = '''
            SELECT PRODUCTS_EMBEDDING.id, PRODUCTS_EMBEDDING.product_embedding, PRODUCTS.img_url, PRODUCTS.product_url, PRODUCTS.SUPER_CATEGORY, PRODUCTS.BASE_CATEGORY
            FROM PRODUCTS_EMBEDDING
            JOIN PRODUCTS ON PRODUCTS_EMBEDDING.ID = PRODUCTS.PRODUCT_ID
            '''

    cursor.execute(sql)
    prod_data = dictfetchall(cursor)

    sql='''
    SELECT STAR_EMBEDDING.STAR_EMBEDDING, STAR.NAME, STAR.STYLE, STAR.CATEGORY
    FROM STAR_EMBEDDING
    JOIN STAR ON STAR.NO=STAR_EMBEDDING.ID
    
    '''

    cursor.execute(sql)
    star_data = dictfetchall(cursor)


    star_cat = list(map(int,star_data[pk]['CATEGORY'].split(',')))
    print('************', star_cat)
    star_name = star_data[pk]['NAME']
    style_no = star_data[pk]['STYLE']
    # emb=np.array(list(map(float, (star_data[pk]['STAR_EMBEDDING'][2:-2].split(',')))))
    # emb2=np.array(list(map(float, (prod_data[0]['PRODUCT_EMBEDDING'][2:-2].split(',')))))

    dist = []
    for i in prod_data:
        if int(i['BASE_CATEGORY']) in star_cat:
            dist.append(
                {
                    'product_id': i['ID'],
                    'distance': compute_linalg_dist(
                        np.array(list(map(float, (star_data[pk]['STAR_EMBEDDING'][2:-2].split(','))))),
                        np.array(list(map(float, (i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                    'img_url': i['IMG_URL'],
                    'product_url': i['PRODUCT_URL']
                }
            )
    dist = sorted(dist, key=lambda x: (x['distance'], x['product_id']))

    if len(dist) > 5:
        context = {"dist": dist[:5], 'star_name': star_name, 'style_no': style_no}
    else:
        context = {"dist": dist, 'star_name': star_name, 'style_no': style_no}

    return render(req, 'products/empty.html', context)




def compute_linalg_dist(img1, img2):
    dist=np.linalg.norm(img1-img2)
    return dist

category_name = [
        {"category": 9, "name": "전체보기"} ,
        {"category": 0, "name": "티셔츠"},
        {"category": 1, "name": "후디/스웨트셔츠"},
        {"category": 2, "name": "셔츠/블라우스"},
        {"category": 3, "name": "니트웨어"},
        {"category": 4, "name": "스커트"},
        {"category": 5, "name": "팬츠"},
        {"category": 6, "name": "데님"},
        {"category": 7, "name": "원피스"},
        {"category": 8, "name": "오버올"}

    ]
category_dict = [
        {"super_category": 0, "category": 0, "sub_category": 0, "name": "롱슬리브"},
        {"super_category": 0, "category": 0, "sub_category": 1, "name": "숏슬리브"},
        {"super_category": 0, "category": 0, "sub_category": 2, "name": "슬리브리스"},
        {"super_category": 0, "category": 0, "sub_category": 3, "name": "크롭 탑"},
        {"super_category": 0, "category": 0, "sub_category": 4, "name": "폴로 셔츠"},
        {"super_category": 0, "category": 1, "sub_category": 5, "name": "후디"},
        {"super_category": 0, "category": 1, "sub_category": 6, "name": "스웨트셔츠"},
        {"super_category": 0, "category": 1, "sub_category": 7, "name": "집업후디"},
        {"super_category": 0, "category": 2, "sub_category": 8, "name": "롱 슬리브"},
        {"super_category": 0, "category": 2, "sub_category": 9, "name": "숏 슬리브"},
        {"super_category": 0, "category": 2, "sub_category": 10, "name": "블라우스"},
        {"super_category": 0, "category": 3, "sub_category": 11, "name": "라운드넥"},
        {"super_category": 0, "category": 3, "sub_category": 12, "name": "브이넥"},
        {"super_category": 0, "category": 3, "sub_category": 13, "name": "터틀넥"},
        {"super_category": 0, "category": 3, "sub_category": 14, "name": "베스트"},
        {"super_category": 0, "category": 3, "sub_category": 15, "name": "가디건"},
        {"super_category": 1, "category": 4, "sub_category": 16, "name": "미니"},
        {"super_category": 1, "category": 4, "sub_category": 17, "name": "미디/롱"},
        {"super_category": 1, "category": 5, "sub_category": 18, "name": "치노"},
        {"super_category": 1, "category": 5, "sub_category": 19, "name": "스웨트팬츠"},
        {"super_category": 1, "category": 5, "sub_category": 20, "name": "스트레이트"},
        {"super_category": 1, "category": 5, "sub_category": 21, "name": "와이드"},
        {"super_category": 1, "category": 5, "sub_category": 22, "name": "스키니"},
        {"super_category": 1, "category": 5, "sub_category": 23, "name": "부츠컷"},
        {"super_category": 1, "category": 5, "sub_category": 24, "name": "쇼츠"},
        {"super_category": 1, "category": 5, "sub_category": 25, "name": "레깅스"},
        {"super_category": 1, "category": 6, "sub_category": 26, "name": "스트레이트"},
        {"super_category": 1, "category": 6, "sub_category": 27, "name": "와이드"},
        {"super_category": 1, "category": 6, "sub_category": 28, "name": "스키니"},
        {"super_category": 1, "category": 6, "sub_category": 29, "name": "부츠컷"},
        {"super_category": 1, "category": 6, "sub_category": 30, "name": "크롭"},
        {"super_category": 1, "category": 6, "sub_category": 31, "name": "스커트"},
        {"super_category": 1, "category": 6, "sub_category": 32, "name": "쇼츠"},
        {"super_category": 2, "category": 7, "sub_category": 33, "name": "미니"},
        {"super_category": 2, "category": 7, "sub_category": 34, "name": "미디/맥시"},
        {"super_category": 2, "category": 7, "sub_category": 35, "name": "드레스"},
        {"super_category": 2, "category": 8, "sub_category": 36, "name": "올인원"},
        {"super_category": 2, "category": 8, "sub_category": 37, "name": "점프수트"}
    ]

def ClientInput(req):
    # static에 저장
    file = req.GET.get('filename')
    filename = file._name
    fp = open(settings.BASE_DIR + f"/static/ClientInput/" + filename, "wb")
    for chunk in file.chunks():
        fp.write(chunk)
    fp.close()