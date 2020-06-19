# django
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.models import OddeyeUsers
from . import embedding
from products.models import Products, ProductsEmbedding
from styles.models import Star, Star_embedding

# db
import cx_Oracle

# 사용할 모듈
import math
import os
import json
import random
import numpy as np


# DB 출력
def dictfetchall(cursor):
    desc = cursor.description
    return [ dict( zip([col[0] for col in desc], row) ) for row in cursor.fetchall()]

# list redirect
def productview(req):
    return redirect('products:prod_list','9')

# Product List
class prod_list(View):
    def get(self, req, pk):
        global base_category_name
        global category_dict

        # DB 연동
        conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        cursor = conn.cursor()

        # Product Data 가져오기
        sql = '''
        SELECT PRODUCTS.super_category, PRODUCTS.base_category, PRODUCTS.sub_category, PRODUCTS.product_ID, PRODUCTS.img_url, PRODUCTS.product_url, PRODUCTS.product_name , PRODUCTS.price_original,PRODUCTS.price_discount,PRODUCTS_EMBEDDING.PRODUCT_EMBEDDING
        FROM Products
        JOIN PRODUCTS_EMBEDDING ON PRODUCTS_EMBEDDING.ID = PRODUCTS.PRODUCT_ID
        '''
        cursor.execute(sql)
        prod_data = dictfetchall(cursor)

        # Star style Data 가져오기
        sql = '''
                SELECT STAR_EMBEDDING.STAR_EMBEDDING, STAR.NAME, STAR.STYLE, STAR.CATEGORY
                FROM STAR_EMBEDDING
                JOIN STAR ON STAR.NO=STAR_EMBEDDING.ID

                '''
        cursor.execute(sql)
        star_data = dictfetchall(cursor)

        # Price Data에 Comma 삽입
        for item in prod_data:
            if item['PRICE_DISCOUNT'] != None:
                item['PRICE_DISCOUNT_COMMA'] = format(item['PRICE_DISCOUNT'], ",")
                item['discounts'] =int( (item['PRICE_ORIGINAL']-item["PRICE_DISCOUNT"])/item['PRICE_ORIGINAL']*100)
            item['PRICE_ORIGINAL_COMMA'] = format(item['PRICE_ORIGINAL'], ",")
        new_dict=[]

        if int(pk)==9:  #전체 상품
            new_dict=prod_data
        else:       #카테고리로 필터링된 상품
            for dt in prod_data:
                if dt['BASE_CATEGORY'] == int(pk):
                    new_dict.append(dt)
        random.shuffle(new_dict) #랜덤한 상품 보여주기
        # Pagination
        paginator = Paginator(new_dict, 30)
        page = req.GET.get("page", 1)
        subs = paginator.get_page(page)

        # 한번에 5개의 페이지씩 보여주기
        page_range = 5
        current_block = math.ceil(int(page) / page_range)
        start_block = (current_block - 1) * page_range
        end_block = start_block + page_range
        p_range = paginator.page_range[start_block:end_block]

        # # 상품과 인물 스타일간 거리 계산
        # emb = {}
        # for p in subs:
        #     emb[p['PRODUCT_ID']] = {
        #         s['NAME'] +'_'+ str(s['STYLE']) : compute_linalg_dist(np.array(list(map(float,(p['PRODUCT_EMBEDDING'][2:-2].split(','))))), np.array(list(map(float,(s['STAR_EMBEDDING'][2:-2].split(',')))))) for s in star_data}
        # sorted_Emb = {}
        # for e in emb:
        #     sorted_Emb[e] = sorted(emb[e].items(), key=lambda x: x[1])[:3]
        #     sorted_Emb[e] = [style_dist_pair[0] for style_dist_pair in sorted_Emb[e]]
        # sorted_s_emb = [{"product_id": product, "likely": sorted_Emb[product]} for product in sorted_Emb]
        #
        # #상품 to 상품
        # products=[]
        # for p in subs:
        #     for d in prod_data:
        #         if p['SUB_CATEGORY'] == d['SUB_CATEGORY']:
        #             products.append(
        #                 {
        #                     'id1': p['PRODUCT_ID'],
        #                     'id2':d['PRODUCT_ID'],
        #                     'dist':compute_linalg_dist(
        #                         np.array(list(map(float,(p['PRODUCT_EMBEDDING'][2:-2].split(','))))),
        #                         np.array(list(map(float,(d['PRODUCT_EMBEDDING'][2:-2].split(','))))))
        #                 }
        #             )
        # products=sorted(products, key=lambda x: (x['id1'], x['dist']))

        #html로 보낼 데이터
        context = {'data': subs, 'cat': base_category_name, 'p_range': p_range} #, 'semb':sorted_s_emb}

        return render(req, 'products/list.html', context)


    def post(self, req, pk):
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


def __str__(self):
    return str(self.nom_asentamiento)

def get_prod_embedding(prod_id):
    prod_id = int(prod_id)
    getem = ProductsEmbedding.objects.filter(product_ID=prod_id).first()
    embedding = getem.product_embedding
    return embedding

def dist_btw_embeddings(emb1, emb2):
    dist = compute_linalg_dist(np.array(list(map(float, (emb1[2:-2].split(','))))),
                        np.array(list(map(float, (emb2[2:-2].split(','))))))
    return dist

def prod2prod(this_prod_embedding, total_prod_data):
    prod_dist = [{'PRODUCT_ID': other_prod['PRODUCT_ID'],
                  'dist': dist_btw_embeddings(this_prod_embedding, other_prod['PRODUCT_EMBEDDING'])} for other_prod in total_prod_data]

    prod_dist = sorted(prod_dist, key=lambda x: x['dist'])
    nearest_prod = prod_dist[1:4]   #자기 자신 제외하고 3개
    nearest_prod_ids = [e['PRODUCT_ID'] for e in nearest_prod]

    # DB 연동
    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()

    # Product Data 가져오기
    sql = '''
        select *
        from PRODUCTS pro
        where pro.product_id in ({}, {}, {})
        '''.format(nearest_prod_ids[0], nearest_prod_ids[1], nearest_prod_ids[2])

    cursor.execute(sql)

    nearest_prod_full_data = dictfetchall(cursor)
    return nearest_prod_full_data

def prod2star(this_prod_embedding, total_star_data):
    print(total_star_data)
    star_dist = [{'no': star.no,
                  'dist': dist_btw_embeddings(this_prod_embedding, star.star_embedding)} for star in
                 total_star_data]
    star_dist = sorted(star_dist, key=lambda x: x['dist'])
    nearest_star = star_dist[:3]
    nearest_star_nos = [e['no'] for e in nearest_star]

    # DB 연동
    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()

    # Product Data 가져오기
    sql = '''
            select *
            from Star
            where Star.no in ({}, {}, {})
            '''.format(nearest_star_nos[0], nearest_star_nos[1], nearest_star_nos[2])

    cursor.execute(sql)

    nearest_star_full_data = dictfetchall(cursor)
    return nearest_star_full_data

def modal_star_and_prod(req):

    prod_id = req.GET['prod_id']
    this_prod_embedding = get_prod_embedding(prod_id)
    # DB 연동
    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()
    # Product Data 가져오기
    # sql = '''
    # select * from product_emb_join_view where product_ID = {}
    # '''.format(prod_id)

    sql = """
    SELECT * 
    FROM PRODUCT_EMB_JOIN_VIEW 
    WHERE BASE_CATEGORY 
    IN (SELECT BASE_CATEGORY FROM PRODUCT_EMB_JOIN_VIEW WHERE product_ID = {})
    """.format(prod_id)

    cursor.execute(sql)
    filtered_prod_data = dictfetchall(cursor)

    # filtered_prod_data = ProductsEmbedding.objects.all()
    total_star_data = Star_embedding.objects.all()

    nearest_prod = prod2prod(this_prod_embedding, filtered_prod_data)
    nearest_star = prod2star(this_prod_embedding, total_star_data)


    return JsonResponse({'error': 0, 'nearest_prod': nearest_prod, 'nearest_star': nearest_star})


def compute_linalg_dist(img1, img2):
    dist=np.linalg.norm(img1-img2)
    return dist
super_category_name=[
    {'category':0, "name":"상의"},
    {'category':1, "name":"상의"},
    {'category':2, "name":"상의"}
]


base_category_name = [
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

class ClientInput(View):
    def get(self, req):
        # cwd = os.getcwd()
        # return render(req, "products/ClientInput.html", {'cwd':cwd})
        return render(req, "products/ClientInput.html")

    def post(self, req):
        file = req.FILES['file1']
        filename = file._name
        fp = open("./static/ClientInput/" + filename, "wb")
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

        amumu = embedding.embedding(img_dir='./static/ClientInput/{}'.format(filename))

        conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        cursor = conn.cursor()
        sql = '''
        SELECT PRODUCTS_EMBEDDING.id, PRODUCTS_EMBEDDING.product_embedding, PRODUCTS.img_url, PRODUCTS.product_url, PRODUCTS.SUPER_CATEGORY, PRODUCTS.BASE_CATEGORY, PRODUCTS.SUB_CATEGORY, PRODUCTS.product_name ,PRODUCTS.price_original,PRODUCTS.price_discount
        FROM PRODUCTS_EMBEDDING
        JOIN PRODUCTS ON PRODUCTS_EMBEDDING.ID = PRODUCTS.PRODUCT_ID
        '''
        cursor.execute(sql)
        prod_data = dictfetchall(cursor)

        dist = []
        for i in prod_data:
            if i['PRICE_DISCOUNT']:
                i['discounts'] = int( (i['PRICE_ORIGINAL'] - i["PRICE_DISCOUNT"]) / i['PRICE_ORIGINAL'] * 100 )
                i['PRICE_DISCOUNT'] = format(i['PRICE_DISCOUNT'], ",")

                dist.append(
                    {
                        'product_name': i['PRODUCT_NAME'],
                        'product_id': i['ID'],
                        'distance': compute_linalg_dist(
                            np.array(list(map(float, (amumu[2:-2].split(','))))),
                            np.array(list(map(float, (i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                        'img_url': i['IMG_URL'],
                        'product_url': i['PRODUCT_URL'],
                        'price_discount': i['PRICE_DISCOUNT'],
                        'price_original': format(i['PRICE_ORIGINAL'], ","),
                        'discounts': i['discounts']
                    }
                )

            else:
                dist.append(
                    {
                        'product_name': i['PRODUCT_NAME'],
                        'product_id': i['ID'],
                        'distance': compute_linalg_dist(
                            np.array(list(map(float, (amumu[2:-2].split(','))))),
                            np.array(list(map(float, (i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                        'img_url': i['IMG_URL'],
                        'product_url': i['PRODUCT_URL'],
                        'price_discount': i['PRICE_DISCOUNT'],
                        'price_original': format(i['PRICE_ORIGINAL'], ","),
                    }
                )

        dist = sorted(dist, key=lambda x: (x['distance'], x['product_id']))

        return render(req, 'products/ClientInputResult.html', {'filename':filename, 'dist':dist[:30], 'amumu':amumu})