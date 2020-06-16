from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse,JsonResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from styles.models import Star
from accounts.models import OddeyeUsers
# from django.db.models import Star
import numpy as np
import cx_Oracle
# from django.db import connection # DB에서 데이터를 받아오기 위한 라이브러리
# from styles.models import star # DB에서 필요한 table import

import os
import random
# Create your views here.
# sql 날려서 받아온 결과를 dict 형태로 만들어주는 함수
def dictfetchall(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

def main(req):
    style_dir='static/img/removed_bg/'
    stars=os.listdir(style_dir)
    imgs=[]
    for j in range(1, 4):
        for i in stars:
            imgs.append({'name':i, 'img':f"{style_dir}{i}/{str(j)}.png", 'thumb':f"static/star/{i}/thumb/{str(j)}.jpg"})
    random.shuffle(imgs)
    thumbnails = random.shuffle(os.listdir('static/step1/star_thumbnails'))
    context = {"data": imgs, "thumbnails": thumbnails}
    return render(req, 'styles/main.html', context)



def StylesList(req, cat_no, KEYWORD=None):
    KEYWORD = req.GET.get('KEYWORD', None)
    print(KEYWORD)
    if KEYWORD == None:
        sql = '''
        SELECT NAME, STYLE, LIKEY
        FROM
        (
        SELECT NAME, STYLE, LIKEY, ROW_NUMBER() OVER(PARTITION BY NAME ORDER BY LIKEY DESC) as rn
        FROM STAR
        )
        WHERE rn <= 1
        '''

    else:
        sql = '''
        SELECT NAME, STYLE, LIKEY
        FROM
        (
        SELECT NAME, STYLE, LIKEY, ROW_NUMBER() OVER(PARTITION BY NAME ORDER BY LIKEY DESC) as rn
        FROM STAR
        )
        WHERE rn <= 1 AND NAME = '{}'
        '''.format(KEYWORD.lower())

    conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
    cursor = conn.cursor()
    cursor.execute(sql)
    db_data = dictfetchall(cursor)

    if len(db_data)==0:
        return HttpResponse('검색 결과가 없으니 돌아가')

    SQL = '''
        SELECT TAG
        FROM STAR
    '''
    cursor.execute(SQL)
    result = cursor.fetchall()

    tags = []
    for r in result:
        tags.append(r[0])
    tags = sorted(list(set(tags)))
    tag_dict=[]
    for t in range(len(tags)):
        tag_dict.append({'tag_name':tags[t],"tag_no":t+1})
    tag_dict=sorted(tag_dict, key=lambda x: (x['tag_no'], x['tag_name']))
    global tagged_star
    if int(cat_no)==0:
        new_data=db_data
    else:
        filtered_star = []
        for star in tagged_star:
            if int(cat_no) in star['tag']:
                filtered_star.append(star['name'])
        new_data=[]
        for data in db_data:
            if data['NAME'] in filtered_star:
                new_data.append(data)

    random.shuffle(db_data)
    page = req.GET.get('page',1)
    p = Paginator(new_data, 6)
    sub = p.page(page)

    context = {'stars':sub, 'tags':tag_dict, "page":page, 'KEYWORD':KEYWORD}
    return render(req, 'styles/list.html', context)

def redirectlist(req):
    return redirect('styles:list','0')

class StarView(View):
    def get(self, req, star_name,pk=1):
        star_name=star_name
        sql = "SELECT style, likey, tag FROM Star WHERE name = '{}' ORDER BY likey desc".format(star_name)
        conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        cursor = conn.cursor()
        cursor.execute(sql)
        db_data = dictfetchall(cursor)

        sql = '''
                SELECT PRODUCTS_EMBEDDING.id, PRODUCTS_EMBEDDING.product_embedding, PRODUCTS.img_url, PRODUCTS.product_url, PRODUCTS.SUPER_CATEGORY, PRODUCTS.BASE_CATEGORY, PRODUCTS.product_name ,PRODUCTS.price_original,PRODUCTS.price_discount
                FROM PRODUCTS_EMBEDDING
                JOIN PRODUCTS ON PRODUCTS_EMBEDDING.ID = PRODUCTS.PRODUCT_ID
                '''
        cursor.execute(sql)
        prod_data = dictfetchall(cursor)
        sql = '''
        SELECT STAR_EMBEDDING.STAR_EMBEDDING, STAR.NAME, STAR.STYLE, STAR.CATEGORY
        FROM STAR_EMBEDDING
        JOIN STAR ON STAR.NO=STAR_EMBEDDING.ID

        '''
        cursor.execute(sql)
        star_data = dictfetchall(cursor)
        star_name = star_name
        style_no = pk
        for s in star_data:
            if s['NAME'] == star_name and int(s['STYLE']) == int(pk):
                star_dict=s
        # print(s['CATEGORY'], star_name, pk)
        star_cat = list(map(int,star_dict['CATEGORY'][1:-1].split(',')))

        dist = []
        for i in prod_data:
            if i['PRICE_DISCOUNT']:
                i['PRICE_DISCOUNT']=format(i['PRICE_DISCOUNT'], ",")
            if int(i['BASE_CATEGORY']) in star_cat:
                dist.append(
                    {
                        'product_name':i['PRODUCT_NAME'],
                        'product_id': i['ID'],
                        'distance': compute_linalg_dist(
                            np.array(list(map(float, (star_dict['STAR_EMBEDDING'][2:-2].split(','))))),
                            np.array(list(map(float, (i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                        'img_url': i['IMG_URL'],
                        'product_url': i['PRODUCT_URL'],
                        'price_discount': i['PRICE_DISCOUNT'],
                        'price_original': format(i['PRICE_ORIGINAL'], ",")
                    }
                )
        dist = sorted(dist, key=lambda x: (x['distance'], x['product_id']))

        # style_num = req.GET.get('sn')
        style_num = pk
        mystyle = Star.objects.all().filter(name=star_name).filter(style=style_num).first()
        cnt = int(mystyle.likey)
        # cnt=0
        fo = star_name + '_' + str(style_num)

        current_user = req.session['username']
        myuser = OddeyeUsers.objects.get(username=current_user)
        myfo = myuser.following

        myfo_set = set(myfo.split(','))
        if fo in myfo_set:
            cklike = True
        else:
            cklike = False


        context = {"star_name":star_name, 'styles': db_data, "cnt":cnt, "cklike":cklike, "dist": dist[:6],'pk':pk, 'star_name': star_name, 'style_no': style_no}
        return render(req, 'styles/detail.html', context)


    def post(self, request, star_name):
        #request.POST.get('key','')
        styles = Star.objects.all()
        style_num = request.POST.get('pk',None)
        mystyle = styles.filter(name=star_name).filter(style=style_num).first()

        cnt = int(mystyle.likey)

        fo = mystyle.name + '_' + str(mystyle.style)
        current_user = request.session['username']
        myuser = OddeyeUsers.objects.get(username=current_user)
        myfo = myuser.following
        myfo_set = set(myfo.split(','))
        if fo in myfo_set:
            cnt -= 1
            myfo_set.discard(fo)
            print('delete {}'.format(fo))
        else:
            cnt += 1
            myfo_set.add(fo)
            print('add {}'.format(fo))
        mystyle.likey = cnt
        mystyle.save()

        myfo_set.discard('')            #빈칸을 element로 갖는 경우가 있어서.
        myfo_set_str = str(myfo_set)
        if len(myfo_set)==0 : myfo_set_str = ''     #빈칸을 set()으로 문자 그대로 넣어서.
        myuser.following = myfo_set_str.replace('{',"").replace('}',"").replace("'","").replace('"',"").replace(" ","").strip(',')
        myuser.save()

        # starpk = req.POST.get('starpk', None)
        # star = get_object_or_404(Star, starpk=starpk)
        # star_like, star_like_created = star.like_set.get_or_create(user=request.user)
        #
        context = {'likes_count':cnt,
                    # 'message':message,
                   }
        return JsonResponse(context)


def compute_linalg_dist(img1, img2):
    dist=np.linalg.norm(img1-img2)
    return dist


tagged_star=[
    {'name': 'soojin', 'tag': [3,12,8,17]},
    {'name': 'goeun', 'tag': [4,3,16,14]},
    {'name': 'irene', 'tag': [12,15,8,6]},
    {'name': 'hani', 'tag': [2,4,15,19]},
    {'name': 'suzy', 'tag': [3,16,15,2]},
    {'name': 'iu', 'tag': [15,14,13,3]},
    {'name': 'hyojin', 'tag': [15,3,5,12]},
    {'name': 'dahee', 'tag': [15,4,15,16]},
    {'name': 'joy', 'tag': [3,16,15,13]},
    {'name': 'hyuna', 'tag': [7,3,18,10]},
    {'name': 'jennie', 'tag': [3,9,1,17]},
    {'name': 'seulgi', 'tag': [6,11,10,16]}
]
