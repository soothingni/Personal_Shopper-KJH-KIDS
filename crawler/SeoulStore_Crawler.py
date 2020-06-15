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
import glob
import re
import sys
from pathlib import Path
import traceback
from builtins import open
import time
from time import sleep

import cx_Oracle

os.environ["NLS_LANG"] = ".AL32UTF8"

options=webdriver.ChromeOptions()     #크롬드라이버 옵션 추가(안 할 시 에러)
options.add_argument('--disable-extensions')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

class SeoulStoreCrawler():
    def __init__(self):
        self.browser = webdriver.Chrome(os.path.dirname(os.path.abspath( __file__ ))+'/chromedriver', chrome_options=options)
        self.browser.implicitly_wait(2)
        self.category_dict = {
            1002: {"super_category": 0, "category": 0, "sub_category": 0, "name": "롱슬리브"},
            1003: {"super_category": 0, "category": 0, "sub_category": 1, "name": "숏슬리브"},
            1004: {"super_category": 0, "category": 0, "sub_category": 2, "name": "슬리브리스"},
            1005: {"super_category": 0, "category": 0, "sub_category": 3, "name": "크롭 탑"},
            1006: {"super_category": 0, "category": 0, "sub_category": 4, "name": "폴로 셔츠"},
            1008: {"super_category": 0, "category": 1, "sub_category": 5, "name": "후디"},
            1010: {"super_category": 0, "category": 1, "sub_category": 6, "name": "스웨트셔츠"},
            1009: {"super_category": 0, "category": 1, "sub_category": 7, "name": "집업후디"},
            1012: {"super_category": 0, "category": 2, "sub_category": 8, "name": "롱 슬리브"},
            1013: {"super_category": 0, "category": 2, "sub_category": 9, "name": "숏 슬리브"},
            1014: {"super_category": 0, "category": 2, "sub_category": 10, "name": "블라우스"},
            1016: {"super_category": 0, "category": 3, "sub_category": 11, "name": "라운드넥" },
            1017: {"super_category": 0, "category": 3, "sub_category": 12, "name": "브이넥"},
            1018: {"super_category": 0, "category": 3, "sub_category": 13, "name": "터틀넥"},
            1019: {"super_category": 0, "category": 3, "sub_category": 14, "name": "베스트"},
            1020: {"super_category": 0, "category": 3, "sub_category": 15, "name": "가디건"},
            
            1025: {"super_category": 1, "category": 4, "sub_category": 16, "name": "미니"},
            1026: {"super_category": 1, "category": 4, "sub_category": 17, "name": "미디/롱"},
            1028: {"super_category": 1, "category": 5, "sub_category": 18, "name": "치노"},
            1034: {"super_category": 1, "category": 5, "sub_category": 19, "name": "스웨트팬츠"},
            1031: {"super_category": 1, "category": 5, "sub_category": 20, "name": "스트레이트"},
            1032: {"super_category": 1, "category": 5, "sub_category": 21, "name": "와이드"},
            1030: {"super_category": 1, "category": 5, "sub_category": 22, "name": "스키니"},
            1033: {"super_category": 1, "category": 5, "sub_category": 23, "name": "부츠컷"},
            1029: {"super_category": 1, "category": 5, "sub_category": 24, "name": "쇼츠"},
            1035: {"super_category": 1, "category": 5, "sub_category": 25, "name": "레깅스"},
            1040: {"super_category": 1, "category": 6, "sub_category": 26, "name": "스트레이트"},
            1041: {"super_category": 1, "category": 6, "sub_category": 27, "name": "와이드"},
            1039: {"super_category": 1, "category": 6, "sub_category": 28, "name": "스키니"},
            1042: {"super_category": 1, "category": 6, "sub_category": 29, "name": "부츠컷"},
            1043: {"super_category": 1, "category": 6, "sub_category": 30, "name": "크롭"},
            1038: {"super_category": 1, "category": 6, "sub_category": 31, "name": "스커트"},
            1037: {"super_category": 1, "category": 6, "sub_category": 32, "name": "쇼츠"},
            
            1022: {"super_category": 2, "category": 7, "sub_category": 33, "name": "미니"},
            1023: {"super_category": 2, "category": 7, "sub_category": 34, "name": "미디/맥시"},
            1273: {"super_category": 2, "category": 7, "sub_category": 35, "name": "드레스"},
            1045: {"super_category": 2, "category": 8, "sub_category": 36, "name": "올인원"},
            1046: {"super_category": 2, "category": 8, "sub_category": 37, "name": "점프수트"}
        }
        # db connection
        self.conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
        self.curs = self.conn.cursor()
    
    def db_insert_with_saleprice(self, row):
        '''
        기능: DB Insert를 처리 시, '제품 할인가'가 포함된다.
        '''
        sql = "insert into products values(:1,:2,:3,:4,:5,:6,:7,:8,:9)"
        self.curs.execute(sql, row)
        print("DB_INSERTED :", row)
        self.conn.commit()

    def db_insert_with_no_saleprice(self, row):
        '''
        기능: DB Insert를 처리 시, '제품 할인가'가 포함되지 않는다.
        '''
        sql = "insert into products(PRODUCT_ID,PRODUCT_NAME,PRICE_ORIGINAL, SUPER_CATEGORY, BASE_CATEGORY, SUB_CATEGORY, IMG_URL, PRODUCT_URL) \
             values(:1, :2, :3, :4, :5, :6, :7, :8)"
        self.curs.execute(sql, row)
        print("DB_INSERTED :", row)
        self.conn.commit()

    def webdriver_close(self):
        '''
        기능 : 크롤링을 위한 크롬 웹드라이버 종료
        '''
        self.browser.close() 

    def crawling_first(self, category_dict, num, filepath):
        '''
        기능 : crawling_first는 최초 DB 등록 시에 사용
        Arguments:
            - category_dict: dict. 카테고리 고유번호: 카테고리 정보 키밸류 페어를 원소로 함
            - num: int. url당 크롤링할 아이템 수
            - filepath: str. 크롤링 결과를 저장할 json 파일 경로
        Return:
            - 없음
        '''
        
        # 중복 크롤링 거르기 위한 셋. product_url을 원소로 함
        product_set = set()

        # category_dict 내 정의된 웹 페이지 별로 크롤링 수행
        for cat in category_dict:
            url = 'https://www.seoulstore.com/categories/{}/regDatetime/desc'.format(str(cat))
            self.browser.get(url)
            body = self.browser.find_element_by_tag_name('body')

            count = 0    #더 이상 로드되는 데이터가 없을 시 크롤링 종료하기 위해 필요한 count임
            prev_posts_count = 0
            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'products_container')))  #페이지 로딩 기다림

            ele_posts = self.browser.find_element_by_class_name('products_container').find_elements_by_class_name('image_container')

            # 원하는 상품의 개수만큼 스크롤 다운
            while len(ele_posts) < num:
                body.send_keys(Keys.PAGE_DOWN)
                ele_posts = self.browser.find_element_by_class_name('products_container').find_elements_by_class_name('ProductItem')

                cur_posts_count = len(ele_posts)
                if prev_posts_count == cur_posts_count:
                    count += 1
                else: count = 0
                if count > 50:
                        break

                prev_posts_count = cur_posts_count

            cat_post_count = 0 # 카테고리별 크롤링된 아이템 수 세기

            for ele in ele_posts:
                product_url= ele.find_element_by_tag_name('a').get_attribute('href')
                key = product_url.split('/')[-2]
                
                if key not in product_set: # 중복 제거, 만약에 set 안에 있으면 수행 안함
                    flag_discount_exists = False
                    dict_post = { "product_url": product_url }
                    dict_post['product_ID'] = int(key)
                    dict_post['product_name'] = ele.find_element_by_class_name('product_name').find_element_by_tag_name('a').text
                    price_list_ele = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')
                    price_1 = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')[-1].text
                    dict_post['price_original'] = int(price_1.replace(',',"").split(' ')[-1])
                    if len(price_list_ele) >= 2:
                        price_2 = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')[0].text
                        dict_post['price_discount'] = int(price_2.replace(',',"").split(' ')[-1])
                        flag_discount_exists = True

                    ele_img = ele.find_element_by_class_name('ImageLoader')
                    dict_post["img_url"] = ele_img.get_attribute("src")
                    
                    dict_post["sub_category"] = category_dict[cat]["sub_category"]
                    dict_post["base_category"] = category_dict[cat]["category"]
                    dict_post["super_category"] = category_dict[cat]["super_category"]

                    cat_post_count +=1
                    product_set.add(key)

                    self.write_json(dict_post, filepath)
                    
                    # 크롤링 내용 Oracle DB에 저장
                    if flag_discount_exists:
                        t = (dict_post['product_ID'], dict_post['product_name'], dict_post['price_original'], dict_post['price_discount'], dict_post['super_category'], dict_post["base_category"], dict_post["sub_category"], dict_post["img_url"], dict_post["product_url"])
                        print(t)
                        self.db_insert_with_saleprice(t)                        
                    else:
                        t = (dict_post['product_ID'], dict_post['product_name'], dict_post['price_original'], dict_post['super_category'], dict_post["base_category"], dict_post["sub_category"], dict_post["img_url"], dict_post["product_url"])
                        print("Test2", t)
                        self.db_insert_with_no_saleprice(t)

            print("saved {} items from {} section".format(cat_post_count, category_dict[cat]['name']))

        self.write_bracket_json(filepath)
        self.webdriver_close()

    def crawling_update(self, category_dict, filepath):
        '''
        기능 : SeoulStore 신상품 출시 시, 크롤링 통해 신상품 DB 업데이트
        Arguments:
            - category_dict: dict. 카테고리 고유번호: 카테고리 정보 키밸류 페어를 원소로 함
            - filepath: str. 크롤링 결과를 저장할 json 파일 경로
        Return:
            - 없음
        '''
        with open(filepath, encoding='UTF8') as data_file:    # 기존 파일 읽어오기
            existing = json.load(data_file)

        product_IDs = [e['product_ID'] for e in existing]
    
        for cat in self.category_dict:
            current_sub_cat = self.category_dict[cat]['sub_category']
            current_cat_product_IDs = [e['product_ID'] for e in existing if e['sub_category'] == current_sub_cat]

            product_set = set(current_cat_product_IDs)
            newest_product_ID = sorted(current_cat_product_IDs, key=lambda x: str(x), reverse=True)[0]   #기존 파일에서 가장 최신 상품의 product_ID

            
            url = 'https://www.seoulstore.com/categories/{}/regDatetime/desc'.format(str(cat))
            self.browser.get(url)
            body = self.browser.find_element_by_tag_name('body')  
            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'products_container')))  #페이지 로딩 기다림
            body.send_keys(Keys.PAGE_DOWN)  #초기 로딩 안 될 때 있어서 한 번 스크롤
            time.sleep(2)
            ele_posts = self.browser.find_element_by_class_name('products_container').find_elements_by_class_name('image_container')
            product_key_temp_first = ele_posts[0].find_element_by_tag_name('a').get_attribute('href').split('/')[-2]

            if product_key_temp_first in product_set: 
                print('{} is up to date'.format(category_dict[cat]['name']))

            else:

                while True:  # 여기서 num은 사용 안 함, 기존 상품이 이미 저장되어 있다는 전제 하에 기존 상품이 보일 때까지 무한
                    ele_posts = self.browser.find_element_by_class_name('products_container').find_elements_by_class_name('ProductItem')
                    new_product_IDs = [e.find_element_by_tag_name('a').get_attribute('href').split('/')[-2] for e in ele_posts]
                    print("new_product_IDs: ", new_product_IDs)
                    print(newest_product_ID in new_product_IDs)

                    # 기존 상품이 보일 시
                    if newest_product_ID in new_product_IDs:
                        break

                    #기존 상품이 안 보일 시 더 스크롤
                    else:
                        _ = [body.send_keys(Keys.PAGE_DOWN) for _ in range(5)]
            
                    cat_post_count = 0   #카테고리별 크롤링된 아이템 수 세기
                    for ele in ele_posts:
                        product_url= ele.find_element_by_tag_name('a').get_attribute('href')
                        key = product_url.split('/')[-2]
                        if key not in product_set:
                            flag_discount_exists = False
                            dict_post = { "product_url": product_url }
                            dict_post['product_ID'] = key
                            dict_post['product_name'] = ele.find_element_by_class_name('product_name').find_element_by_tag_name('a').text
                            price_list_ele = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')
                            price_1 = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')[-1].text
                            dict_post['price_original'] = int(price_1.replace(',',"").split(' ')[-1])
                            if len(price_list_ele) >= 2:
                                price_2 = ele.find_element_by_class_name('price').find_elements_by_css_selector('span')[0].text
                                dict_post['price_discount'] = int(price_2.replace(',',"").split(' ')[-1])
                                flag_discount_exists = True

                            ele_img = ele.find_element_by_class_name('ImageLoader')
                            dict_post["img_url"] = ele_img.get_attribute("src")

                            dict_post["sub_category"] = category_dict[cat]["sub_category"]
                            dict_post["category"] = category_dict[cat]["category"]
                            dict_post["super_category"] = category_dict[cat]["super_category"]   

                            cat_post_count +=1
                            product_set.add(key)
                            
                            self.write_add_json(dict_post, filepath)
                            
                            # 크롤링 내용 Oracle DB에 저장
                            # if flag_discount_exists:
                            #     t = (dict_post['product_ID'], dict_post['product_name'], dict_post['price_original'], dict_post['price_discount'], dict_post['super_category'], dict_post["base_category"], dict_post["sub_category"], dict_post["img_url"], dict_post["product_url"])
                            #     print(t)
                            #     self.db_insert_with_saleprice(t)                        
                            # else:
                            #     t = (dict_post['product_ID'], dict_post['product_name'], dict_post['price_original'], dict_post['super_category'], dict_post["base_category"], dict_post["sub_category"], dict_post["img_url"], dict_post["product_url"])
                            #     print("Test2", t)
                            #     self.db_insert_with_no_saleprice(t)  
                                            
        self.webdriver_close()

    def write_json(self, dict_post, filepath):
        '''
        기능 : Crawling 한 내용을 json 포맷으로 만든다.
        input : dict_post
        output : json files
        '''
        out = json.dumps(dict_post, ensure_ascii=False)    #json 형식으로 정보 변환
        out += ', '    #아이템 정보 분류하기 위해 끝에 쉼표 추가


        # 크롤링 내용 categorized.json에 저장
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(out)
    
    def write_bracket_json(self, filepath):
        # []로 감싸주기
        with open(filepath, encoding="utf-8") as f:
            file = f.read()

        removed_comma = file[:-2]
        bracketed = '[' + removed_comma + ']'

        with open(filepath, 'w', encoding = 'utf-8') as f:
            f.write(bracketed)

    def write_add_json(self, dict_post, filepath):
        # 업데이트 내역 새로 저장할 경로
        base_path='/root/Personal_Shopper-KJH-KIDS/crawler/crawling_logs'
        now = time.localtime()
        Path('/new_only_' + time.strftime('%y%m%d_%H', now) +  '.json').touch()
        new_filepath = './new_only_' + time.strftime('%y%m%d_%H', now) +  '.json'

        print(time.strftime('start at %Y-%m-%d %I:%M:%S %p', time.localtime()))  

        out = json.dumps(dict_post, ensure_ascii=False)    #json 형식으로 정보 변환
        out += ', '    #아이템 정보 분류하기 위해 끝에 쉼표 추가
        if not os.path.exists(new_filepath):
            with open(new_filepath, "w", encoding="utf-8") as f:
                f.write(out)
        else:
            with open(new_filepath, "a", encoding="utf-8") as f:
                f.write(out)


    @staticmethod
    def download_single_file(fileURL, key):
        print('Downloading image...')
        DIR='../web/oddeye/static/img/seoulstore_ALL'
        if not os.path.exists(DIR):
            os.mkdir(DIR)
        fileName = DIR + '/' + str(key) + '.jpg'
        urllib.request.urlretrieve(fileURL, fileName)
        print('Done. ' + fileName)
                    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--isFirst', default="True",
                        help="Crawling for the first time or not")
    parser.add_argument('--num', default=1000,
                        help="Number of items to fetch per category")
    parser.add_argument('--filepath', default='./crawling_logs/categorized_tong.json',
                        help="Directory to save item info")
                        
    args = parser.parse_args()

    crawler = SeoulStoreCrawler()
#     print('-------------------------------------------------------')
#     print('Starting PROCESS 1: Fetching item info')
#     print('-------------------------------------------------------')

#     mode = args.isFirst
    
#     if mode == "True":
#         print("Initial Save Starts!")
#         crawler.crawling_first(crawler.category_dict, int(args.num), args.filepath)
#     else:
#         print("Update Starts!")
#         crawler.crawling_update(crawler.category_dict, args.filepath)
       

    print('-------------------------------------------------------')
    print('Starting PROCESS 2: Image Download')
    print('-------------------------------------------------------')

    filepath = args.filepath
    with open(filepath, encoding='utf-8') as data_file:
        data = json.load(data_file)

    count = 0
    for i in range(len(data)):
        imgURL = data[i]['img_url']
        key = data[i]['product_ID']
        crawler.download_single_file(imgURL, key)
        count += 1
    print("Successfully downloaded {} images".format(count))
