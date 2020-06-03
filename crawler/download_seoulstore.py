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
import time
import traceback
from builtins import open
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument('--isfirst', default=False,
                    help="Crawling for the first time or not")
parser.add_argument('--num', default=1000,
                    help="Number of items to fetch per category")
parser.add_argument('--filepath', default='categorized_tong.json',
                    help="Directory to save item info")

category_dict = {
    1002: {"super_category": 0, "category": 0, "sub_category": 0, "name": "롱슬리브"},
    1003: {"super_category": 0, "category": 0, "sub_category": 1, "name": "숏슬리브"},
    1004: {"super_category": 0, "category": 0, "sub_category": 2, "name": "슬리브리스"},
    1005: {"super_category": 0, "category": 0, "sub_category": 3, "name": "크롭 탑"},
    1006: {"super_category": 0, "category": 0, "sub_category": 4, "name": "폴로 셔츠"},
    1008: {"super_category": 0, "category": 1, "sub_category": 5, "name": "후디"},
    1010: {"super_category": 0, "category": 1, "sub_category": 6, "name": "스웨트셔츠"},
    1009: {"super_category": 0, "category": 1, "sub_category": 7, "name": "집업후디"},
    1012: {"super_category": 0, "category": 2, "sub_category": 8, "name": "롱 슬리브"},
    1013:{"super_category": 0, "category": 2, "sub_category": 9, "name": "숏 슬리브"},
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

    wait_time = 300
    browser = webdriver.Chrome('chromedriver')   #크롬 브라우저 실행
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
        for ele in ele_posts:
            product_url= ele.find_element_by_tag_name('a').get_attribute('href')
            key = product_url.split('/')[-2]
            if key not in product_set:
                try:
                    dict_post = { "product_url": product_url }
                    dict_post['key'] = key
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ImageLoader.ratio_1_1.loaded')))
                    ele_img = ele.find_element_by_class_name('ImageLoader.ratio_1_1.loaded')
                    dict_post["img_url"] = ele_img.get_attribute("src")
                    dict_post["sub_category"] = category_dict[cat]["sub_category"]
                    dict_post["category"] = category_dict[cat]["category"]
                    dict_post["super_category"] = category_dict[cat]["super_category"]
                    product_set.add(key)
                    
                    if isfirst == True: pass
                    else:    #첫번째 크롤링 아닐 경우 저장 경로 바꿈
                        now = time.localtime()
                        filepath_temp = '_'.join(os.path.splitext(filepath)[0].split('_')[:-2])
                        filepath = filepath_temp +'_'+time.strftime('%y%m%d_%I%M%S', now) + os.path.splitext(filepath)[1]
                    
                    out = json.dumps(dict_post, ensure_ascii=False)    #json 형식으로 정보 변환
                    out += ', '    #아이템 정보 분류하기 위해 끝에 쉼표 추가
                    with open(filepath, "a", encoding="utf-8") as f:
                        f.write(out)
                    cat_post_count +=1
                
                except: continue
        print("saved {} items from {} section{}".format(cat_post_count, category_dict[cat]['name'], isntfirst_txt))
   
    #[]로 감싸주기
    with open(filepath, encoding="utf-8") as f:
        file = f.read()

    removed_comma = file[:-1]
    bracketed = '[' + removed_comma + ']'

    with open(filepath, 'w', encoding = 'utf-8') as f:
        f.write(bracketed)
        
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
    
    product_set = set([e['key'] for e in existing])   #중복 크롤링 거르기 위한 셋. product_url을 원소로 함
    
    #새로 저장할 경로
    now = time.localtime()
    filepath_temp = '_'.join(os.path.splitext(filepath)[0].split('_')[:-2])
    new_filepath = filepath_temp +'_'+time.strftime('%y%m%d_%I%M%S', now) + os.path.splitext(filepath)[1]

    wait_time = 300
    browser = webdriver.Chrome('chromedriver')   #크롬 브라우저 실행
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
        product_url_temp_first = ele_posts[0].find_element_by_tag_name('a').get_attribute('href')
        if product_url_temp_first in product_set: print('{} is up to date'.format(category_dict[cat]['name']))
            
        while True:  # 여기서 num은 사용 안 함, 기존 상품이 이미 저장되어 있다는 전제 하에 기존 상품이 보일 때까지 무한
            ele_posts = browser.find_element_by_class_name('products_container').find_elements_by_class_name('image_container')
            product_url_temp_last = ele_posts[-1].find_element_by_tag_name('a').get_attribute('href')
                
            # 기존 상품이 보일 시
            if product_url_temp_last in product_set: break
                
            #기존 상품이 안 보일 시 더 스크롤
            else: _=[body.send_keys(Keys.PAGE_DOWN) for _ in range(5)]
            
        
    cat_post_count = 0   #카테고리별 크롤링된 아이템 수 세기
    for ele in ele_posts:
        product_url= ele.find_element_by_tag_name('a').get_attribute('href')
        key = product_url.split('/')[-2]
        if key not in product_set:
            try:
                dict_post = { "product_url": product_url }
                dict_post['key'] = key
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ImageLoader.ratio_1_1.loaded')))
                ele_img = ele.find_element_by_class_name('ImageLoader.ratio_1_1.loaded')
                dict_post["img_url"] = ele_img.get_attribute("src")
                dict_post["sub_category"] = category_dict[cat]["sub_category"]
                dict_post["category"] = category_dict[cat]["category"]
                dict_post["super_category"] = category_dict[cat]["super_category"]
                product_set.add(key)
                    
                out = json.dumps(dict_post, ensure_ascii=False)    #json 형식으로 정보 변환
                out += ', '    #아이템 정보 분류하기 위해 끝에 쉼표 추가
                with open(new_filepath, "a", encoding="utf-8") as f:
                    f.write(out)
                cat_post_count +=1
                
            except: continue
        
    print("saved {} new items from {} section{}".format(cat_post_count, category_dict[cat]['name']))
    
    #[]로 감싸주기
    with open(new_filepath, encoding="utf-8") as f:
        file = f.read()

    removed_comma = file[:-1]
    bracketed = '[' + removed_comma + ']'

    with open(filepath, 'w', encoding='utf-8') as f:       #기존 파일에 새로 크롤링한 내용 덧붙이기
        total_file = existing.extend(bracketed)
        f.write(total_file)

    with open(new_filepath, 'w', encoding = 'utf-8') as f:    #새로 크롤링한 내용만 담긴 파일 생성
        f.write(bracketed)

    print('Finished updating. Saved as {}'.format(new_filepath))
    browser.close()
    return new_filepath

def DownloadSingleFile(fileURL, key):
    print('Downloading image...')
    DIR = f'./seoulstore_ALL'
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
    if args.isfirst == True:
        get_products1(category_dict, args.num, args.filepath)
        filepath = args.filepath

    else:
        new_filepath = get_products2(category_dict, args.filepath)
        filepath = new_filepath
    print('-------------------------------------------------------')
    print('Starting PROCESS 2: Image Download')
    print('-------------------------------------------------------')


    with open(filepath) as data_file:
        data = json.load(data_file)

    count = 0
    for i in range(len(data)):
        imgURL = data[i]['img_url']
        key = data[i]['key']
        DownloadSingleFile(imgURL, key)
        count += 1
    print("Successfully downloaded {} images".format(count))