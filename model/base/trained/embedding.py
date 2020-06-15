import tensorflow as tf

from tensorflow.keras import backend as K
from tensorflow.keras.layers import Input, BatchNormalization, LSTM, Dense, concatenate, Conv2D, MaxPooling2D, Flatten, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import plot_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50, ResNet101

import argparse
import numpy as np
import random
import matplotlib.pyplot as plt
import os
import cv2
import json
import glob
from skimage import io
from tqdm import tqdm


import cx_Oracle
import os
os.environ["NLS_LANG"] = ".AL32UTF8"

# db connection
conn = cx_Oracle.connect('oddeye/1234@15.164.247.135:1522/MODB')
curs = conn.cursor()

parser = argparse.ArgumentParser()
parser.add_argument('--model_dir', default='./resnet101_detectron/000001-1.6717.h5',
                    help="Model weights dir")
parser.add_argument('--img_dir', default='/root/Personal_Shopper-KJH-KIDS/web/oddeye/static/img/seoulstore_ALL',
                    help="Images dir")
parser.add_argument('--table', default='products_embedding',
                    help="table to insert embedding")

def lossless_triplet_loss(y_true, y_pred, N=128, beta=128, epsilon=1e-8):
    """
    Implementation of the triplet loss function
    
    Arguments:
    y_true -- true labels, required when you define a loss in Keras, you don't need it in this function.
    y_pred -- python list containing three objects:
            anchor -- the encodings for the anchor data
            positive -- the encodings for the positive data (similar to anchor)
            negative -- the encodings for the negative data (different from anchor)
    N  --  The number of dimension 
    beta -- The scaling factor, N is recommended
    epsilon -- The Epsilon value to prevent ln(0)
    
    
    Returns:
    loss -- real number, value of the loss
    """
    anchor = tf.convert_to_tensor(y_pred[:,0:N])
    positive = tf.convert_to_tensor(y_pred[:,N:N*2]) 
    negative = tf.convert_to_tensor(y_pred[:,N*2:N*3])
    
    # distance between the anchor and the positive
    pos_dist = tf.reduce_sum(tf.square(tf.subtract(anchor,positive)),1)
    # distance between the anchor and the negative
    neg_dist = tf.reduce_sum(tf.square(tf.subtract(anchor,negative)),1)
    
    #Non Linear Values  
    
    # -ln(-x/N+1)
    pos_dist = -tf.math.log(-tf.divide((pos_dist),beta)+1+epsilon)
    neg_dist = -tf.math.log(-tf.divide((N-neg_dist),beta)+1+epsilon)
    
    # compute loss
    loss = neg_dist + pos_dist
    
    
    return loss

def res_base_network(in_dims, out_dims, res_ver):
    model = Sequential()
    
    if res_ver == "resnext101":
        model.add(ResNeXt101(
        include_top=False, weights='imagenet', input_shape=in_dims, pooling='avg', classes=1000,
        backend = tf.keras.backend, layers = tf.keras.layers, models = tf.keras.models, utils = tf.keras.utils))
        
    elif res_ver == "resnet50":
        model.add(ResNet50(
    include_top=False, weights='imagenet', input_shape=in_dims, pooling='avg', classes=1000))
        
    elif res_ver =="resnet101":
         model.add(ResNet101(
    include_top=False, weights='imagenet', input_shape=in_dims, pooling='avg', classes=1000))

    model.add(Dense(1024, activation = 'relu'))
    model.add(Dense(out_dims, activation = 'sigmoid'))

    return model        
        
def create_res_model(res_ver):
    in_dims = (224, 224, 3)  # (28, 28, 1)
    out_dims = 128

    # Create the 3 inputs
    anchor_in = Input(shape=in_dims, name='anchor')
    pos_in = Input(shape=in_dims, name='positive')
    neg_in = Input(shape=in_dims, name='negative')

    # with tf.compat.v1.Session(config=config):
    # Share base network with the 3 inputs
    base_network = res_base_network(in_dims, out_dims, res_ver)
    anchor_out = base_network(anchor_in)
    pos_out = base_network(pos_in)
    neg_out = base_network(neg_in)

    merged_vector = concatenate([anchor_out, pos_out, neg_out], axis=-1)

    # Define the trainable model
    model = Model(inputs=[anchor_in, pos_in, neg_in], outputs=merged_vector)
    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss=lossless_triplet_loss)
    
    return base_network, model

def freeze_layer(base, reverse_index):
    for layer in base.layers[0].layers[:reverse_index]:
        layer.trainable=False

    for layer in base.layers[0].layers[reverse_index:]:
        layer.trainable=True
    
    cnt = 0
    for layer in base.layers[0].layers:
        if layer.trainable: cnt +=1
    print('traninable layers in ResNet: {}'.format(cnt))

def db_insert(t, count, table):
    sql=f"insert into {table} values(:1,:2,:3)"
    curs.execute(sql,t)
#     print(f"Insertion executed! {count}")
    conn.commit()
    
def get_style_num(star, num):
    sql = f'''
    SELECT no FROM Star WHERE name = '{star}' AND style = '{num}'
    '''
    curs.execute(sql)
    style_num = dictfetchall(cursor)
    return style_num
      
def encode_img_by_path(img_path, base_network):
#     image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)   #cv2.imread() 가끔 오류생겨서 아래로 바꿈
    image = io.imread(img_path, plugin='matplotlib')
    image = cv2.resize(image, (224, 224))
    if image.shape[-1] == 4: #4채널일 경우 마지막 채널 제외
        image = image[:, :, :-1]        
    image_encoding = base_network.predict(np.array([image]))
    image_encoding = np.around(image_encoding, 10)    #소숫점 아래 10째자리까지 라운드
    image_encoding = image_encoding.tolist()
    return image_encoding

if __name__ == '__main__':
    args = parser.parse_args()
    model_dir = args.model_dir
    img_dir = args.img_dir
    table = args.table
    
    print('-------------------------------------------------------')
    print('Starting PROCESS 1: Creating model...')
    print('-------------------------------------------------------')
    
    base, model = create_res_model("resnet101")
    base.layers[0].trainable=False
    
    print('Created model frame')
    
    print("Started loading weights from {}".format(model_dir))
    model.load_weights(model_dir)
    print("Weights loaded. Finished creating model")
    
    print('-------------------------------------------------------')
    print('Starting PROCESS 2: Started embedding items')
    print('-------------------------------------------------------')
    
#     data_path = os.path.join(img_dir,'*g')
#     files = glob.glob(data_path)
#     file_count = len(files)
    
#     print("Found {} images from {}".format(file_count, img_dir))

    stars = os.listdir(img_dir)
    print(f"Found {len(stars)}")
    
    cnt = 0
    
    for star in stars:
        star_name = star.split('/')[-1]
        files = os.listdir(img_dir + '/' + star)
        
        for i in tqdm(range(len(files))):
            file_name = files[i].split('/')[-1]
            file_name, _ = os.path.splitext(file_name)
            
            style_num = get_style_num(star_name, file_name)

            encoding = encode_img_by_path(files[i], base)
            encoding = str(encoding)

            cnt += 1
            t = (style_num, encoding, style_num)

            db_insert(t, cnt, table)