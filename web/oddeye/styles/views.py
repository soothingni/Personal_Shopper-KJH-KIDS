# django 기능 import
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse,JsonResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Sum
from styles.models import Star
from accounts.models import OddeyeUsers

# DB import
import cx_Oracle

# 필요한 모듈 import
import os
import random
import numpy as np

# DB data 가져오기
def dictfetchall(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

# Main Page
def main(req):
    if req.method =="GET":
        style_dir='static/img/removed_bg/'
        stars=os.listdir(style_dir)
        imgs=[]
        for j in range(1, 4):
            for i in stars:
                imgs.append({'name':i, 'img':f"{style_dir}{i}/{str(j)}.png", 'thumb':f"static/star/{i}/thumb/{str(j)}.jpg"})
        random.shuffle(imgs)

        # 스타 추천
        star_name = "irene"
        pk = "4"
        sql = "SELECT style, likey, tag FROM Star WHERE name = '{}' ORDER BY likey desc".format(star_name)
        conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        cursor = conn.cursor()
        cursor.execute(sql)
        db_data_star = dictfetchall(cursor)

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
        for s in star_data:
            if s['NAME'] == star_name and int(s['STYLE']) == int(pk):
                star_dict = s
        star_cat = list(map(int, star_dict['CATEGORY'][1:-1].split(',')))

        dist = []
        for i in prod_data:
            if i['PRICE_DISCOUNT']:
                i['discounts'] = int((i['PRICE_ORIGINAL'] - i["PRICE_DISCOUNT"]) / i['PRICE_ORIGINAL'] * 100)
                i['PRICE_DISCOUNT'] = format(i['PRICE_DISCOUNT'], ",")

            if int(i['BASE_CATEGORY']) in star_cat:
                if i["PRICE_DISCOUNT"]:
                    dist.append(
                        {
                            'PRODUCT_NAME': i['PRODUCT_NAME'],
                            'PRODUCT_ID': i['ID'],
                            'distance': compute_linalg_dist(
                                np.array(list(map(float, (star_dict['STAR_EMBEDDING'][2:-2].split(','))))),
                                np.array(list(map(float, (i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                            'IMG_URL': i['IMG_URL'],
                            'PRODUCT_URL': i['PRODUCT_URL'],
                            'PRICE_DISCOUNT': i['PRICE_DISCOUNT'],
                            'PRICE_ORIGINAL': format(i['PRICE_ORIGINAL'], ","),
                            'discounts': i['discounts']

                        }
                    )
                else:
                    dist.append(
                        {
                            'PRODUCT_NAME': i['PRODUCT_NAME'],
                            'PRODUCT_ID': i['ID'],
                            'distance': compute_linalg_dist(
                                np.array(list(map(float, (star_dict['STAR_EMBEDDING'][2:-2].split(','))))),
                                np.array(list(map(float, (i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                            'IMG_URL': i['IMG_URL'],
                            'PRODUCT_URL': i['PRODUCT_URL'],
                            'PRICE_DISCOUNT': i['PRICE_DISCOUNT'],
                            'PRICE_ORIGINAL': format(i['PRICE_ORIGINAL'], ","),

                        }
                    )

        dist = sorted(dist, key=lambda x: (x['distance'], x['PRODUCT_ID']))

        style_num = pk
        mystyle = Star.objects.all().filter(name=star_name).filter(style=style_num).first()
        cnt = int(mystyle.likey)

        fo = star_name + '_' + str(style_num)
        # 상품 리스트
        sql = '''
                SELECT super_category, base_category, sub_category, product_ID,img_url, product_url,product_name ,price_original,price_discount
                FROM PRODUCTS WHERE rownum <= 8
                '''
        conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        cursor = conn.cursor()
        cursor.execute(sql)
        db_data = dictfetchall(cursor)

        for item in db_data:
            if item['PRICE_DISCOUNT']:
                item['discounts'] = int(
                    (item['PRICE_ORIGINAL'] - item["PRICE_DISCOUNT"]) / item['PRICE_ORIGINAL'] * 100)
                item['PRICE_DISCOUNT_COMMA'] = format(item['PRICE_DISCOUNT'], ",")
            item['PRICE_ORIGINAL_COMMA'] = format(item['PRICE_ORIGINAL'], ",")
        random.shuffle(db_data)
        if req.user.is_authenticated == True:
            current_user = req.session['username']
            myuser = OddeyeUsers.objects.get(username=current_user)
            myfo = myuser.following

            myfo_set = set(myfo.split(','))
            if fo in myfo_set:
                cklike = True
            else:
                cklike = False



            context = {
                "data": imgs,
                'datas': db_data,
                "star_name": star_name,
                'styles': db_data_star,
                "cnt": cnt,
                "cklike": cklike,
                "dist": dist[:6],
                'pk': pk,
                'style_no': pk
            }
        else:
            context={
                "data":imgs,
                "star_name":star_name,
                "styles":db_data_star,
                "pk":pk,
                "style_no":pk,
                "dist":dist[:6],
                "datas":db_data,
                "cnt":cnt
            }
        return render(req, 'styles/main.html', context)

    if req.method == "POST":
        star_name = "irene"
        styles = Star.objects.all()
        style_num = request.POST.get('pk', None)
        mystyle = styles.filter(name=star_name).filter(style=style_num).first()

        cnt = int(mystyle.likey)
        fo = mystyle.name + '_' + str(mystyle.style)
        if req.user.is_authenticated == True:
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

            myfo_set.discard('')  # 빈칸을 element로 갖는 경우가 있어서.
            myfo_set_str = str(myfo_set)
            if len(myfo_set) == 0: myfo_set_str = ''  # 빈칸을 set()으로 문자 그대로 넣어서.
            myuser.following = myfo_set_str.replace('{', "").replace('}', "").replace("'", "").replace('"', "").replace(" ",',')
            myuser.save()
            context = {'likes_count': cnt}
        else:
            context={}
        return JsonResponse(context)


def StylesList(req, cat_no, KEYWORD=None):
    KEYWORD = req.GET.get('KEYWORD', None)
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
        return HttpResponse(
            '''
        검색 결과가 없으니 <a href="/styles/">돌아가</a>
        '''
        )
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
        star_cat = list(map(int,star_dict['CATEGORY'][1:-1].split(',')))

        dist = []
        for i in prod_data:
            if i['PRICE_DISCOUNT']:
                i['discounts'] = int((i['PRICE_ORIGINAL'] - i["PRICE_DISCOUNT"]) / i['PRICE_ORIGINAL'] * 100)
                i['PRICE_DISCOUNT']=format(i['PRICE_DISCOUNT'], ",")

            if int(i['BASE_CATEGORY']) in star_cat:
                if i["PRICE_DISCOUNT"]:
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
                            'price_original': format(i['PRICE_ORIGINAL'], ","),
                            'discounts':i['discounts']

                        }
                    )
                else:
                    dist.append(
                        {
                            'product_name': i['PRODUCT_NAME'],
                            'product_id': i['ID'],
                            'distance': compute_linalg_dist(
                                np.array(list(map(float, (star_dict['STAR_EMBEDDING'][2:-2].split(','))))),
                                np.array(list(map(float, (i['PRODUCT_EMBEDDING'][2:-2].split(',')))))),
                            'img_url': i['IMG_URL'],
                            'product_url': i['PRODUCT_URL'],
                            'price_discount': i['PRICE_DISCOUNT'],
                            'price_original': format(i['PRICE_ORIGINAL'], ","),

                        }
                    )

        dist = sorted(dist, key=lambda x: (x['distance'], x['product_id']))

        style_num = pk
        mystyle = Star.objects.all().filter(name=star_name,style=style_num).first()
        cnt = int(mystyle.likey)
        total_cnt = Star.objects.all().filter(name=star_name).aggregate(likey_sum=Sum('likey'))['likey_sum']


        fo = star_name + '_' + str(style_num)
        if req.user.is_authenticated == True:
            current_user = req.session['username']
            myuser = OddeyeUsers.objects.get(username=current_user)
            myfo = myuser.following

            myfo_set = set(myfo.split(','))
            if fo in myfo_set:
                cklike = True
            else:
                cklike = False

            context = {"star_name":star_name, 'styles': db_data, "cnt":cnt, "total_cnt": total_cnt, "cklike":cklike, "dist": dist[:30],'pk':pk,'style_no': style_no}

        else:
            context = {"star_name": star_name, 'styles': db_data, "cnt": cnt, "total_cnt": total_cnt,
                       "dist": dist[:30], 'pk': pk, 'style_no': style_no}
        return render(req, 'styles/detail.html', context)


    def post(self, req, star_name):
        if req.user.is_authenticated == True:
            styles = Star.objects.all()
            style_num = req.POST.get('pk',None)
            mystyle = styles.filter(name=star_name).filter(style=style_num).first()

            cnt = int(mystyle.likey)

            fo = mystyle.name + '_' + str(mystyle.style)
            current_user = req.session['username']
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
            context = {'likes_count':cnt }
        else:
            context = {}
        return JsonResponse(context)

def compute_linalg_dist(img1, img2):
    dist=np.linalg.norm(img1-img2)
    return dist

# 1 : 내추럴, 2 : 데일리, 3 : 러블리, 4 : 럭셔리, 5 : 레트로, 6 : 미니멀,
# 7 : 빈티지, 8 : 센슈얼, 9 : 스포티, 10 : 시크, 11 : 어반, 12 : 에스닉,
# 13 : 애슬레져, 14 : 큐트, 15 : 페미닌, 16 : 포멀, 17 : 하이틴, 18 : 힙, 19 : 힙합
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
