import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Input, BatchNormalization, LSTM, Dense, concatenate, Conv2D, MaxPooling2D, Flatten, GlobalAveragePooling2D, Activation
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.utils import plot_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50, ResNet101
from keras_applications.resnext import ResNeXt101


import numpy as np
import random
import matplotlib.pyplot as plt
import os
import cv2
import json
import glob


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
    anchor = tf.convert_to_tensor(y_pred[:, 0:N])
    positive = tf.convert_to_tensor(y_pred[:, N:N * 2])
    negative = tf.convert_to_tensor(y_pred[:, N * 2:N * 3])

    # distance between the anchor and the positive
    pos_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, positive)), 1)
    # distance between the anchor and the negative
    neg_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, negative)), 1)

    # Non Linear Values

    # -ln(-x/N+1)
    pos_dist = -tf.math.log(-tf.divide((pos_dist), beta) + 1 + epsilon)
    neg_dist = -tf.math.log(-tf.divide((N - neg_dist), beta) + 1 + epsilon)

    # compute loss
    loss = neg_dist + pos_dist

    return loss


def cnn_base_network(in_dims, out_dims):
    model = Sequential()

    model.add(Conv2D(input_shape=in_dims,
                     filters=10, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu'))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3), activation='relu'))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3), activation='sigmoid'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())  # 1차원화

    model.add(Dense(32, activation='relu'))
    model.add(Dense(out_dims, activation='sigmoid'))

    return model

def cnn_base_network2(in_dims, out_dims, activation='sigmoid'):
    model = Sequential()

    model.add(Conv2D(input_shape = in_dims,
                     filters = 10, kernel_size = (3,3), strides = (1,1), padding = 'same'))
    
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    
    model.add(Conv2D(64, (3, 3)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(256, (3, 3)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(256, (3, 3)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(512, (3, 3)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(512, (3, 3)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(GlobalAveragePooling2D())

    model.add(Dense(1024, activation = 'relu'))

    model.add(Dense(out_dims, activation = activation))

    return model

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

#     model.add(Dense(1024, activation = 'relu'))

    model.add(Dense(1024))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(Dense(out_dims, activation = 'sigmoid'))

    return model

def create_model():
    in_dims = (150, 150, 4)  # (28, 28, 1)
    out_dims = 128

    # Create the 3 inputs
    anchor_in = Input(shape=in_dims, name='anchor')
    pos_in = Input(shape=in_dims, name='positive')
    neg_in = Input(shape=in_dims, name='negative')

    # with tf.compat.v1.Session(config=config):
    # Share base network with the 3 inputs
    base_network = cnn_base_network(in_dims, out_dims)
    anchor_out = base_network(anchor_in)
    pos_out = base_network(pos_in)
    neg_out = base_network(neg_in)

    merged_vector = concatenate([anchor_out, pos_out, neg_out], axis=-1)

    # Define the trainable model
    model = Model(inputs=[anchor_in, pos_in, neg_in], outputs=merged_vector)
    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss=lossless_triplet_loss)
    
    return base_network, model

def create_model2(activation='sigmoid'):
    in_dims = (150, 150, 4)  # (28, 28, 1)
    out_dims = 128

    # Create the 3 inputs
    anchor_in = Input(shape=in_dims, name='anchor')
    pos_in = Input(shape=in_dims, name='positive')
    neg_in = Input(shape=in_dims, name='negative')

    # with tf.compat.v1.Session(config=config):
    # Share base network with the 3 inputs
    base_network = cnn_base_network2(in_dims, out_dims, activation=activation)
    anchor_out = base_network(anchor_in)
    pos_out = base_network(pos_in)
    neg_out = base_network(neg_in)

    merged_vector = concatenate([anchor_out, pos_out, neg_out], axis=-1)

    # Define the trainable model
    model = Model(inputs=[anchor_in, pos_in, neg_in], outputs=merged_vector)
    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss=lossless_triplet_loss)
    
    return base_network, model

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
#     model.compile(optimizer=Adam(learning_rate=0.0001),
#                   loss=lossless_triplet_loss)
    
    return base_network, model

def get_file_names(img_dir):
    data_path = os.path.join(img_dir,'*g')
    files = glob.glob(data_path)
    file_names = [os.path.basename(file_name) for file_name in files]
    return file_names

def load_images(img_dir, num_img):
    data_path = os.path.join(img_dir,'*g')
    files = glob.glob(data_path)[:num_img]
    images = {os.path.basename(file_name): cv2.resize(cv2.cvtColor(cv2.imread(file_name), cv2.COLOR_BGR2RGB), (224, 224)) for file_name in files} 
    return images

def encode_items(imgs, base_network):
    encodings = { key: base_network.predict(np.array([imgs[key]])) for key in imgs}
    return encodings

def create_encoding_file(masked_img_dir, base_network, out_filepath, img_dim):
    data_path = os.path.join(masked_img_dir,'*g')
    files = glob.glob(data_path)
    
    for file in files:
#         if os.path.splitext(file)[-1] in ['.jpg', '.jpeg', '.png', '.gif']:
        image = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        if type(image) == np.ndarray:    #파일 제대로 읽어왔을 때만 실행
            if img_dim[-1] == 4:    #학습시킨 채널이 4개일 때
                image = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA), img_dim[:-1], interpolation=cv2.INTER_CUBIC)
            else:
                image = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), img_dim[:-1])
            image_encoding = base_network.predict(np.array([image])).tolist()
            key = os.path.basename(file).split('.')[0]
            out = json.dumps({"key":key, "encoding": image_encoding}, ensure_ascii=False)
            out += ', '
            with open(out_filepath, "a", encoding = "utf-8") as f:
                f.write(out)
            
   #[]로 감싸주기
    with open(out_filepath, encoding="utf-8") as f:
        file = f.read()
        
    removed_comma = file[:-2]
    bracketed = '[' + removed_comma + ']'

    with open(out_filepath, 'w', encoding='utf-8') as f:       #기존 파일에 새로 크롤링한 내용 덧붙이기
        f.write(bracketed)
            
def compute_log_dist(img1, img2):
    dist = tf.reduce_sum(tf.square(tf.subtract(img1, img2)),1)
    dist = -tf.math.log(-tf.divide((dist),128)+1+1e-8)
    dist = dist.numpy()[0]
    return dist

def compute_linalg_dist(img1, img2):
    dist = np.linalg.norm(img1-img2)
    return dist

def show_similar_items(encoding_file, origin_img_dir, dist_mode='log', thresh=0.1, display_num=3):
    with open(encoding_file, encoding='utf-8') as f:
        data_list = json.load(f)
        
    img_names = [data['key'] for data in data_list]
    encodings = {data['key'] : np.asarray(data['encoding']) for data in data_list}    #파일에서 인코딩 값 --> 넘파이 어레이

    for img in img_names:
        #anchor
        anchor_encoding = encodings[img]
        
        anchor_dir = os.path.join(origin_img_dir, img + '.*g')
        anchor_dir = glob.glob(anchor_dir)[0]
        anchor_image = cv2.cvtColor(cv2.imread(anchor_dir), cv2.COLOR_BGR2RGB)

        plt.imshow(anchor_image)
        plt.xlabel("Anchor: {}".format(img))
        plt.show()
        
        distance_dict = {}
        sim = []
        
        #anchor와 다른 이미지들 대조
        for img in img_names:
            img_encoding = encodings[img]
            dist = compute_log_dist(anchor_encoding, img_encoding) if dist_mode == 'log' else compute_linalg_dist(anchor_encoding, img_encoding)
            distance_dict[img] = dist
            if (dist < thresh) and (dist != 0):
                sim.append(img)

        sorted_distance = sorted(distance_dict.items(), key=(lambda x: x[1]))   #거리순으로 정렬
        sorted_distance = sorted_distance[1:]       # 동일 이미지 제거

        plt.figure(figsize=(display_num*3, 3))

        #비슷한 상품을 찾지 못한 경우 --> 그나마 유사한 display_num개 상품을 거리순으로 보여줌
        if len(sim) == 0:
            print("No similar items found.\nDisplaying nearest {} items.".format(display_num))
            for k in range(display_num):
                key, dist = sorted_distance[k]
                img_dir = os.path.join(origin_img_dir, key + '.*g')
                img_dir = glob.glob(img_dir)[0]
                img_image = cv2.cvtColor(cv2.imread(img_dir), cv2.COLOR_BGR2RGB)
                plt.subplot(1, display_num, k+1)
                plt.imshow(img_image)
                plt.xlabel('{}, {:.4f}'.format(key, dist))
            plt.show()

        #비슷한 상품을 찾았으나, 개수가 display_num 미만인 경우 --> 찾은만큼만 거리순으로 보여줌
        elif len(sim) < display_num:
            print("Found {} similar items.".format(len(sim)))
            for k in range(len(sim)):
                key, dist = sorted_distance[k]
                img_dir = os.path.join(origin_img_dir, key + '.*g')
                img_dir = glob.glob(img_dir)[0]
                img_image = cv2.cvtColor(cv2.imread(img_dir), cv2.COLOR_BGR2RGB)
                plt.subplot(1, display_num, k+1)
                plt.imshow(img_image)
                plt.xlabel('{}, {:.4f}'.format(key, dist))
            plt.show()

        #비슷한 상품을 display_num 이상으로 찾은 경우 --> display_num개 비슷한 상품을 거리순으로 보여줌
        else:
            print("Found {} similar items.".format(len(sim)))
            for k in range(display_num):
                key, dist = sorted_distance[k]
                img_dir = os.path.join(origin_img_dir, key + '.*g')
                img_dir = glob.glob(img_dir)[0]
                img_image = cv2.cvtColor(cv2.imread(img_dir), cv2.COLOR_BGR2RGB)
                plt.subplot(1, display_num, k+1)
                plt.imshow(img_image)
                plt.xlabel('{}, {:.4f}'.format(key, dist))
            plt.show()
            
def show_similar_items_by_designated_pi(designated_pi, encoding_file, origin_img_dir, dist_mode='log', thresh=0.1, display_num=3):
    with open(encoding_file, encoding='utf-8') as f:
        data_list = json.load(f)
        
    img_names = [data['key'] for data in data_list]
    encodings = {data['key'] : np.asarray(data['encoding']) for data in data_list}    #파일에서 인코딩 값 --> 넘파이 어레이

    for img in designated_pi:
        #anchor
        try:
            anchor_encoding = encodings[img]

            anchor_dir = os.path.join(origin_img_dir, img + '.*g')
            anchor_dir = glob.glob(anchor_dir)[0]
            anchor_image = cv2.cvtColor(cv2.imread(anchor_dir), cv2.COLOR_BGR2RGB)

            plt.imshow(anchor_image)
            plt.xlabel("Anchor: {}".format(img))
            plt.show()

            distance_dict = {}
            sim = []

            #anchor와 다른 이미지들 대조
            for img in img_names:
                img_encoding = encodings[img]
                dist = compute_log_dist(anchor_encoding, img_encoding) if dist_mode == 'log' else compute_linalg_dist(anchor_encoding, img_encoding)
                distance_dict[img] = dist
                if (dist < thresh) and (dist != 0):
                    sim.append(img)

            sorted_distance = sorted(distance_dict.items(), key=(lambda x: x[1]))   #거리순으로 정렬s
            sorted_distance = sorted_distance[1:]       # 동일 이미지 제거

            plt.figure(figsize=(display_num*3, 3))

            #비슷한 상품을 찾지 못한 경우 --> 그나마 유사한 display_num개 상품을 거리순으로 보여줌
            if len(sim) == 0:
                print("No similar items found.\nDisplaying nearest {} items.".format(display_num))
                for k in range(display_num):
                    key, dist = sorted_distance[k]
                    img_dir = os.path.join(origin_img_dir, key + '.*g')
                    img_dir = glob.glob(img_dir)[0]
                    img_image = cv2.cvtColor(cv2.imread(img_dir), cv2.COLOR_BGR2RGB)
                    plt.subplot(1, display_num, k+1)
                    plt.imshow(img_image)
                    plt.xlabel('{}, {:.4f}'.format(key, dist))
                plt.show()

            #비슷한 상품을 찾았으나, 개수가 display_num 미만인 경우 --> 찾은만큼만 거리순으로 보여줌
            elif len(sim) < display_num:
                print("Found {} similar items.".format(len(sim)))
                for k in range(len(sim)):
                    key, dist = sorted_distance[k]
                    img_dir = os.path.join(origin_img_dir, key + '.*g')
                    img_dir = glob.glob(img_dir)[0]
                    img_image = cv2.cvtColor(cv2.imread(img_dir), cv2.COLOR_BGR2RGB)
                    plt.subplot(1, display_num, k+1)
                    plt.imshow(img_image)
                    plt.xlabel('{}, {:.4f}'.format(key, dist))
                plt.show()

            #비슷한 상품을 display_num 이상으로 찾은 경우 --> display_num개 비슷한 상품을 거리순으로 보여줌
            else:
                print("Found {} similar items.".format(len(sim)))
                for k in range(display_num):
                    key, dist = sorted_distance[k]
                    img_dir = os.path.join(origin_img_dir, key + '.*g')
                    img_dir = glob.glob(img_dir)[0]
                    img_image = cv2.cvtColor(cv2.imread(img_dir), cv2.COLOR_BGR2RGB)
                    plt.subplot(1, display_num, k+1)
                    plt.imshow(img_image)
                    plt.xlabel('{}, {:.4f}'.format(key, dist))
                plt.show()
                
        except:
            print('couldn\'t find designated product in masked images')