# -*- coding: utf-8 -*- 

import urllib.request
import json
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import glob
import json
import os
import re
import sys
from pathlib import Path
import traceback
from builtins import open
from time import sleep

import cx_Oracle
import os
os.environ["NLS_LANG"] = ".AL32UTF8"

base_path = '/root/Personal_Shopper-KJH-KIDS/crawler/UpdateProduct'

# db connection
conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
curs = conn.cursor()

parser = argparse.ArgumentParser()
parser.add_argument('--isfirst', default=None,
                    help="Crawling for the first time or not")
parser.add_argument('--num', default=1000,
                    help="Number of items to fetch per category")
parser.add_argument('--filepath', default=base_path+'/categorized_tong.json',
                    help="Directory to save item info")

category_dict = {
    1002: {"super_category": 0, "category": 0, "sub_category": 0, "name": "롱슬리브"},
#     1003: {"super_category": 0, "category": 0, "sub_category": 1, "name": "숏슬리브"},
#     1004: {"super_category": 0, "category": 0, "sub_category": 2, "name": "슬리브리스"},
#     1005: {"super_category": 0, "category": 0, "sub_category": 3, "name": "크롭 탑"},
#     1006: {"super_category": 0, "category": 0, "sub_category": 4, "name": "폴로 셔츠"},
#     1008: {"super_category": 0, "category": 1, "sub_category": 5, "name": "후디"},
#     1010: {"super_category": 0, "category": 1, "sub_category": 6, "name": "스웨트셔츠"},
#     1009: {"super_category": 0, "category": 1, "sub_category": 7, "name": "집업후디"},
#     1012: {"super_category": 0, "category": 2, "sub_category": 8, "name": "롱 슬리브"},
#     1013:{"super_category": 0, "category": 2, "sub_category": 9, "name": "숏 슬리브"},
#     1014: {"super_category": 0, "category": 2, "sub_category": 10, "name": "블라우스"},
#     1016: {"super_category": 0, "category": 3, "sub_category": 11, "name": "라운드넥" },
#     1017: {"super_category": 0, "category": 3, "sub_category": 12, "name": "브이넥"},
#     1018: {"super_category": 0, "category": 3, "sub_category": 13, "name": "터틀넥"},
#     1019: {"super_category": 0, "category": 3, "sub_category": 14, "name": "베스트"},
#     1020: {"super_category": 0, "category": 3, "sub_category": 15, "name": "가디건"},
    
#     1025: {"super_category": 1, "category": 4, "sub_category": 16, "name": "미니"},
#     1026: {"super_category": 1, "category": 4, "sub_category": 17, "name": "미디/롱"},
#     1028: {"super_category": 1, "category": 5, "sub_category": 18, "name": "치노"},
#     1034: {"super_category": 1, "category": 5, "sub_category": 19, "name": "스웨트팬츠"},
#     1031: {"super_category": 1, "category": 5, "sub_category": 20, "name": "스트레이트"},
#     1032: {"super_category": 1, "category": 5, "sub_category": 21, "name": "와이드"},
#     1030: {"super_category": 1, "category": 5, "sub_category": 22, "name": "스키니"},
#     1033: {"super_category": 1, "category": 5, "sub_category": 23, "name": "부츠컷"},
#     1029: {"super_category": 1, "category": 5, "sub_category": 24, "name": "쇼츠"},
#     1035: {"super_category": 1, "category": 5, "sub_category": 25, "name": "레깅스"},
#     1040: {"super_category": 1, "category": 6, "sub_category": 26, "name": "스트레이트"},
#     1041: {"super_category": 1, "category": 6, "sub_category": 27, "name": "와이드"},
#     1039: {"super_category": 1, "category": 6, "sub_category": 28, "name": "스키니"},
#     1042: {"super_category": 1, "category": 6, "sub_category": 29, "name": "부츠컷"},
#     1043: {"super_category": 1, "category": 6, "sub_category": 30, "name": "크롭"},
#     1038: {"super_category": 1, "category": 6, "sub_category": 31, "name": "스커트"},
#     1037: {"super_category": 1, "category": 6, "sub_category": 32, "name": "쇼츠"},
    
#     1022: {"super_category": 2, "category": 7, "sub_category": 33, "name": "미니"},
#     1023: {"super_category": 2, "category": 7, "sub_category": 34, "name": "미디/맥시"},
#     1273: {"super_category": 2, "category": 7, "sub_category": 35, "name": "드레스"},
#     1045: {"super_category": 2, "category": 8, "sub_category": 36, "name": "올인원"},
    1046: {"super_category": 2, "category": 8, "sub_category": 37, "name": "점프수트"}
}

def db_insert(t, count):
    sql="insert into products values(:1,:2,:3,:4,:5,:6)"
    curs.execute(sql,t)
    print(f"Insertion executed! {count}")
    conn.commit()

def get_products1(category_dict, num, filepath):
    
    """
    Arguments:
    - category_dict: dict. 카테고리 고유번호: 카테고리 정보 키밸류 페어를 원소로 함
    - num: int. url당 크롤링할 아이템 수
    - filepath: str. 크롤링 결과를 저장할 json 파일 경로
    
    Return:
    - 없음
    """
    product_set = set()   #중복 크롤링 거르기 위한 셋. product_url을 원소로 함

    path='/home/ubuntu/chromedriver'    #크롬드라이버 경로

    wait_time = 300
    options=webdriver.ChromeOptions()     #크롬드라이버 옵션 추가(안 할 시 에러)
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    browser=webdriver.Chrome(path, chrome_options=options)  #드라이버 생성
    # browser = webdriver.Chrome('chromedriver')   #크롬 브라우저 실행
    wait = WebDriverWait(browser, wait_time)
    
    for cat in category_dict:
        url = 'https://www.seoulstore.com/categories/{}/regDatetime/desc'.format(str(cat))
        browser.get(url)
        body = browser.find_element_by_tag_name('body')

        count = 0    #더 이상 로드되는 데이터가 없을 시 크롤링 종료하기 위해 필요한 count임
        prev_posts_count = 0
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'products_container')))  #페이지 로딩 기다림
        time.sleep(2)
        ele_posts = browser.find_element_by_class_name('products_container').find_elements_by_class_name('image_container')
            
        ##########추가한 부분###########
        while len(ele_posts) < num:
            body.send_keys(Keys.PAGE_DOWN)
            ele_posts = browser.find_element_by_class_name('products_container').find_elements_by_class_name('image_container')

            cur_posts_count = len(ele_posts)
            if prev_posts_count == cur_posts_count:
                count += 1
            else: count = 0
            if count > 50:
                    break

            prev_posts_count = cur_posts_count
        ##########추가한 부분 끝##########
       
        cat_post_count = 0   #카테고리별 크롤링된 아이템 수 세기
        
        print(len(ele_posts))
        
        for ele in ele_posts:
            product_url= ele.find_element_by_tag_name('a').get_attribute('href')
            key = product_url.split('/')[-2]
            if key not in product_set:
                try:
                    dict_post = { "product_url": product_url }
                    dict_post['product_id'] = key
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ImageLoader.ratio_1_1.loaded')))
                    ele_img = ele.find_element_by_class_name('ImageLoader.ratio_1_1.loaded')
                    dict_post["img_url"] = ele_img.get_attribute("src")
                    dict_post["sub_category"] = category_dict[cat]["sub_category"]
                    dict_post["base_category"] = category_dict[cat]["category"]
                    dict_post["super_category"] = category_dict[cat]["super_category"]

                    dict_post['product_name'] = ele.find_element_by_class_name('product_name').find_element_by_tag_name('a').text
                    price_list_ele = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')
                    price_1 = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')[-1].text
                    dict_post['price_consumer'] = int(price_1.replace(',',""))
                    if len(price_list_ele) >= 2:
                        price_2 = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')[0].text
                        dict_post['price_discount'] = int(price_2.replace(',',""))

                    product_set.add(key)
                    
                    out = json.dumps(dict_post, ensure_ascii=False)    #json 형식으로 정보 변환
                    out += ', '    #아이템 정보 분류하기 위해 끝에 쉼표 추가

                    with open(filepath, "a", encoding="utf-8") as f:
                        f.write(out)
                    cat_post_count +=1
                    
                    t = (dict_post['product_id'], dict_post['super_category'], dict_post["base_category"], dict_post["sub_category"], dict_post["img_url"], dict_post["product_url"])   
                    print("Test", t)
                    db_insert(t, cat_post_count)

                except: continue
                    
        print("saved {} items from {} section".format(cat_post_count, category_dict[cat]['name']))
   
    #[]로 감싸주기
    with open(filepath, encoding="utf-8") as f:
        file = f.read()

    removed_comma = file[:-2]
    bracketed = '[' + removed_comma + ']'

    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(bracketed)

    # #product_id 순으로 정렬(내림차순)
    # with open(filepath) as json_file:
    #     jsonfile = json.load(json_file)
    #
    # sorted_json = sorted(jsonfile, key=lambda x: x['product_id'], reverse=True)
    #
    # with open('sorted_' + filepath, 'w') as f:
    #     f.write(str(sorted_json))

    print('Finished crawling. Saved as {}'.format(filepath))
    browser.close()
    
def get_products2(category_dict, filepath):
    
    """
    Arguments:
    - category_dict: dict. 카테고리 고유번호: 카테고리 정보 키밸류 페어를 원소로 함
    - filepath: str. 기존 크롤링 결과가 저장된 json 파일 경로
    
    Return:
    - 없음
    """
    with open(filepath) as data_file:    # 기존 파일 읽어오기
        existing = json.load(data_file)

    product_ids = [e['product_ID'] for e in existing]
    newest_product_id = sorted(product_ids, key=lambda x: str(x), reverse=True)[0]   #기존 파일에서 가장 최신 상품의 product_id
    product_set = set(product_ids)   #중복 크롤링 거르기 위한 셋. key를 원소로 함
          
    #새로 저장할 경로
    now = time.localtime()
    Path(base_path+'/new_only_' + time.strftime('%y%m%d_%H', now) +  '.json').touch()
    new_filepath = base_path+'/new_only_' + time.strftime('%y%m%d_%H', now) +  '.json'

    wait_time = 300
    path = '/home/ubuntu/chromedriver'
    options=webdriver.ChromeOptions()     #크롬드라이버 옵션 추가(안 할 시 에러)
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    browser=webdriver.Chrome(path, chrome_options=options)  #드라이버 생성
    wait = WebDriverWait(browser, wait_time)
    
    print(time.strftime('start at %Y-%m-%d %I:%M:%S %p', time.localtime()))    
    for cat in category_dict:
        url = 'https://www.seoulstore.com/categories/{}/regDatetime/desc'.format(str(cat))
        browser.get(url)
        body = browser.find_element_by_tag_name('body')  
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'products_container')))  #페이지 로딩 기다림
        body.send_keys(Keys.PAGE_DOWN)  #초기 로딩 안 될 때 있어서 한 번 스크롤
        time.sleep(2)
        ele_posts = browser.find_element_by_class_name('products_container').find_elements_by_class_name('image_container')
        product_key_temp_first = ele_posts[0].find_element_by_tag_name('a').get_attribute('href').split('/')[-2]

        if product_key_temp_first in product_set: 
            print('{} is up to date'.format(category_dict[cat]['name']))

        else:
            
            while True:  # 여기서 num은 사용 안 함, 기존 상품이 이미 저장되어 있다는 전제 하에 기존 상품이 보일 때까지 무한
                ele_posts = browser.find_element_by_class_name('products_container').find_elements_by_class_name('image_container')
                new_product_ids = [e.find_element_by_tag_name('a').get_attribute('href').split('/')[-2] for e in ele_posts]

                # 기존 상품이 보일 시
                if newest_product_id in new_product_ids:
                    break

                #기존 상품이 안 보일 시 더 스크롤
                else:
                    _ = [body.send_keys(Keys.PAGE_DOWN) for _ in range(5)]
            
        
            cat_post_count = 0   #카테고리별 크롤링된 아이템 수 세기
            for ele in ele_posts:
                product_url= ele.find_element_by_tag_name('a').get_attribute('href')
                key = product_url.split('/')[-2]
                if key not in product_set:
                    try:
                        dict_post = { "product_url": product_url }
                        dict_post['product_id'] = key
                        ele_img = ele.find_element_by_class_name('ImageLoader.ratio_1_1.loaded')
                        dict_post["img_url"] = ele_img.get_attribute("src")
                        dict_post["sub_category"] = category_dict[cat]["sub_category"]
                        dict_post["category"] = category_dict[cat]["category"]
                        dict_post["super_category"] = category_dict[cat]["super_category"]
                        product_set.add(key)

                        out = json.dumps(dict_post, ensure_ascii=False)    #json 형식으로 정보 변환
                        out += ', '    #아이템 정보 분류하기 위해 끝에 쉼표 추가
                        if not os.path.exists(new_filepath):
                            with open(new_filepath, "w", encoding="utf-8") as f:
                                f.write(out)
                        else:
                            with open(new_filepath, "a", encoding="utf-8") as f:
                                f.write(out)
                        cat_post_count +=1
                        
                        t = (dict_post['product_id'], dict_post['super_category'], dict_post["base_category"], dict_post["sub_category"], dict_post["img_url"], dict_post["product_url"])   
                        print("Test", t)
                        db_insert(t, cat_post_count)

                    except:
                        continue

            print("saved {} new items from {} section".format(cat_post_count, category_dict[cat]['name']))

            #[]로 감싸주기
            with open(new_filepath, encoding="utf-8") as f:
                file = f.read()

            removed_comma = file[:-2]
            bracketed = '[' + removed_comma + ']'

            with open(new_filepath, 'w', encoding='utf-8') as f:    #새로 크롤링한 내용만 있는 파일 (이미지 다운로드용)
                f.write(str(bracketed))

            with open(new_filepath, encoding='utf-8') as data_file:
                new_data = json.load(data_file)

            with open(filepath, 'w', encoding='utf-8') as f:       #기존 파일에 새로 크롤링한 내용 덧붙이기
                existing.extend(new_data)
                f.write(str(existing))

            print('Finished updating. Saved as {}'.format(new_filepath))

    browser.close()
    
    return new_filepath

def DownloadSingleFile(fileURL, key):
    print('Downloading image...')
    DIR = '../web/oddeye/static/img/seoulstore_ALL'
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    fileName = DIR + '/' + str(key) + '.jpg'
    urllib.request.urlretrieve(fileURL, fileName)
    print('Done. ' + fileName)

    
if __name__ == '__main__':
    args = parser.parse_args()
    print('-------------------------------------------------------')
    print('Starting PROCESS 1: Fetching item info')
    print('-------------------------------------------------------')

    print(args.isfirst)
    
    if args.isfirst:
        get_products1(category_dict, int(args.num), args.filepath)
        filepath = args.filepath
        print('isfirst is true')

    else:
        new_filepath = get_products2(category_dict, args.filepath)
        filepath = new_filepath
        print('isfirst is false')
        
    curs.close()
    conn.commit()
    conn.close()
        
    print('-------------------------------------------------------')
    print('Starting PROCESS 2: Image Download')
    print('-------------------------------------------------------')

    print(filepath)        
    with open(filepath) as data_file:
        data = json.load(data_file)

    count = 0
    for i in range(len(data)):
        imgURL = data[i]['img_url']
        key = data[i]['product_id']
        DownloadSingleFile(imgURL, key)
        count += 1
    print("Successfully downloaded {} images".format(count))
