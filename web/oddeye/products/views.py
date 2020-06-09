from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

''' 여기는 django db (sqlite) 사용할 때 필요한 모듈?
from django.db import connection # DB에서 데이터를 받아오기 위한 라이브러리
from products.models import product # DB에서 필요한 table import
'''

import os
import json
import random
# Create your views here.

# DB에서 불러온 데이터를 field명(img_url, product_url)과 결합하기 위한 함수. 수업 내용 확인
def dictfetchall(cursor):
    desc = cursor.description
    return [ dict( zip([col[0] for col in desc], row) ) for row in cursor.fetchall()]

def ProductsList(req):
    # DB 연동 후 사용할 코드
    '''
    sql = """
        SELECT img_url, product_url
        FROM products_product
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    result = dictfetchall(cursor)
    '''
    
    # 임시 코드
    result = [{'img_url': 'https://images.seoulstore.com/products/52a6ed2a1d61b21e79e0f3a5c1f03263.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/955954/detail'},
    {'img_url': 'https://images.seoulstore.com/products/c04a10c862fed49321b275886ff91596.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1178222/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/0405007e66dcf5326511bfac12df5750.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1176995/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/908c5394532f98d5767ab5d66dc97011.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1140124/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/f6a009306fd662e1a625552083add81e.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1195070/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/a637b6181f729bbe93a7a45b3e6b4d10.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1176903/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/9fa426c6866fc5204b7843b42e4a744a.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1178231/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/a2222fb3c79a0e1f84262dc87d15e7c7.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1164131/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/d4457c40b02a98e88cd6de0f7118e789.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1124440/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/abdb62faa5a63abf6554af760ca70ec1.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1090758/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/836dc22990414b2363738e02edfc2247.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1084665/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/e6e916b8767faf961a72431ca7e6e2ae.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1085926/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/35842beb1ad4b6fcd5202b02333105bf.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1211852/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/408a3a869063179cb93fca47ea8ad75e.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1211850/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/f835cc7affe8bcb8c9387d388f2af038.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1210494/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/ecea23edc14e8be8a928a5a35b8395b8.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1209181/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/c9850e490c50a14d9a55a41ccadeed97.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1207956/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/92e64c94573c3af3c874fc8f250ce65f.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1206717/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/1b0fb2ec874d8a444df2d1ef724cb98d.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1206668/detail'}, 
    {'img_url': 'https://images.seoulstore.com/products/db7ef21fb50b25cddeae02b3135c383e.jpg?d=640xauto', 'product_url': 'https://www.seoulstore.com/products/1206211/detail'}]

    page = req.GET.get('page', 1)
    NUMBER_OF_DATAS_PER_ONCE = 8
    paginator = Paginator(result, NUMBER_OF_DATAS_PER_ONCE) # 한 페이지에 해당 개수만큼을 할당
    
    try:
        datas = paginator.page(page)
    except PageNotAnInteger:
        datas = paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)
    
    print(datas[0])


    return render(req, 'products/list.html', {'datas': datas})

def modaltest(req):
    return render(req, 'products/modaltest.html')





def productview(req):
    with open('static/json/categorized_tong.json', 'r') as json_file:
        json_data=json.load(json_file)
    page=req.GET.get("page",1)
    p=Paginator(json_data,12)
    subs=p.page(page)
    context={'data':subs}
    return render(req,'products/json_test.html', context)



def prod_init(req):
    with open('static/json/categorized_tong.json', 'r') as json_file:
        json_data=json.load(json_file)
    page=req.GET.get("page",1)
    p=Paginator(json_data,12)
    subs=p.page(page)
    context={'data':subs}
    return render(req,'products/prod_in.html', context)