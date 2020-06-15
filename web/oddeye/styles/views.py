from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse,JsonResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from styles.models import Star
from accounts.models import OddeyeUsers
# from django.db.models import Star

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
            imgs.append({'name':i, 'img':f"{style_dir}{i}/{str(j)}.png", 'thumb':f"static/star/{i}/thumb/{str(j)}.jpg"})
    thumbnails = os.listdir('static/step1/star_thumbnails')
    context = {"data": imgs, "thumbnails": thumbnails}
    return render(req, 'styles/main.html', context)

def StylesList(req, KEYWORD=None):
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
    # print(db_data)

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
    # tag_dict=dict(zip(tags,[x for x in range(1,20)]))
    tag_dict=sorted(tag_dict, key=lambda x: (x['tag_no'], x['tag_name']))
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

    tags = set(tags)
    # print(tags)
    page = req.GET.get('page',1)
    p = Paginator(db_data, 6)
    sub = p.page(page)
    context = {'stars':sub, 'tags':tag_dict, "page":page, 'KEYWORD':KEYWORD}
    # print(context)
    return render(req, 'styles/list.html', context)

def style_filter(req, cat_no):
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
    tags = sorted(list(set(tags)))
    tag_dict=[]
    for t in range(len(tags)):
        tag_dict.append({'tag_name':tags[t],"tag_no":t+1})
    # tag_dict=dict(zip(tags,[x for x in range(1,20)]))
    tag_dict=sorted(tag_dict, key=lambda x: (x['tag_no'], x['tag_name']))
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

    context = {'stars':sub, 'tags':tag_dict, "page":page}
    # print(context)

    return render(req, 'styles/list_filtered.html', context)










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

    def post(self, request, star_name):
        print(star_name)
        styles = Star.objects.all()
        mystyle = styles.filter(name=star_name).filter(style='1').first()

        cnt = int(mystyle.likey)


        fo = mystyle.name + '_' + str(mystyle.style)
        current_user = request.session['username']
        myuser = OddeyeUsers.objects.get(username=current_user)
        myfo = myuser.following
        myfo_list = myfo.strip('[]').split(',')
        print(myfo_list)
        if fo in myfo_list:
            cnt -= 1
            mystyle.likey = cnt
            mystyle.save()

            myfo_list.remove(fo)
            myuser.following = str(myfo_list)
            myuser.save()
        else:
            cnt += 1
            mystyle.likey = cnt
            mystyle.save()

            myfo_list = myuser.following.strip('[]').split(',')
            myfo_list.append(fo)
            myuser.following = str(myfo_list)
            myuser.save()






        # starpk = req.POST.get('starpk', None)
        # star = get_object_or_404(Star, starpk=starpk)
        # star_like, star_like_created = star.like_set.get_or_create(user=request.user)
        #
        # if not star_like_created:
        #     star_like.delete()
        #     message = "좋아요 취소"
        # else:
        #     message = "좋아요"
        # context = {'like_count': star.like_count,
        #            'message' : message,
        #            'nickname': request.uesr.profile.nickname}
        context = {'likes_count':cnt,
                    # 'message':message,
                   }
        return JsonResponse(context)
