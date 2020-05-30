import urllib.request
import json
import os

def DownloadSingleFile(fileURL, key):
    print('Downloading image...')
    DIR = f'./seoulstore_ALL'
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    fileName = DIR + '/' + str(key) + '.jpg'
    urllib.request.urlretrieve(fileURL, fileName)
    print('Done. ' + fileName)


if __name__ == '__main__':

    with open('categorized_tong.json') as data_file:
        data = json.load(data_file)
    count = 0
    for i in range(len(data)):
        instagramURL = data[i]['img_url']
        key = data[i]['key']
        DownloadSingleFile(instagramURL, key)
        count += 1
    print("Successfully downloaded {} images".format(count))