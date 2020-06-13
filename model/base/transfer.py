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


parser = argparse.ArgumentParser()
parser.add_argument('--resver', default="resnet101",
                    help="backbone resnet version")
parser.add_argument('--previous_unfreeze', default=346,
                    help="Old reverse index of unfrozen resnet layers in weights to load")
parser.add_argument('--current_unfreeze', default=-11,
                    help="New reverse index of resnet layers to unfreeze")
parser.add_argument('--weights_dir', default='./trained/resnet101_detectron_val/000330-1.3812-4.8970.h5',
                    help="weights dir")
parser.add_argument('--epochs', default=1000,
                    help="Number of epochs to train model")
parser.add_argument('--steps', default=100,
                    help="Num of steps per epochs")
# parser.add_argument('--model_path', default='temp',
#                     help="Directory name to save model")
parser.add_argument('--batch_size', default=4,
                    help="Batch size")

gen = ImageDataGenerator(rescale=1./255)
train_data_dir = '../train'
val_data_dir = '../val'
directory = os.listdir(train_data_dir)
CLASS_DICT = {k:v for k, v in enumerate(directory)}
num_classes = len(CLASS_DICT)


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

def res_base_network(in_dims, out_dims, activation='sigmoid'):
    model = Sequential()
    
    model.add(ResNet101(
    include_top=False, weights='imagenet', input_shape=in_dims, pooling='avg', classes=1000))

    model.add(Dense(1024, activation = 'relu'))
    model.add(Dense(out_dims, activation = activation))

    return model

def input_triplet_gen(gen, data_dir, num_classes, batch_size):
    
    while True:
        anchor_label, neg_label = random.sample(range(0, num_classes), 2)
        
        POS_DIR = os.path.join(data_dir, CLASS_DICT[anchor_label])
        NEG_DIR = os.path.join(data_dir, CLASS_DICT[neg_label])
        
        POS_filecount = len(os.listdir(os.path.join(POS_DIR, POS_DIR.split(os.path.sep)[-1])))    #POS_DIR 파일 개수 (뎁스 2번 들어가야해서 os.path.join~ 해주기)
        NEG_filecount = len(os.listdir(os.path.join(NEG_DIR, NEG_DIR.split(os.path.sep)[-1])))   #NEG_DIR 파일 개수
        
        if  POS_filecount < batch_size or NEG_filecount < batch_size:    #파일 개수가 batch_size 미만이면 처음으로 돌아가서 클래스 다시 선택
            continue

        anchor_gen = gen.flow_from_directory(POS_DIR, 
                                             target_size=(224, 224),
                                             batch_size=batch_size,
                                             color_mode='rgb')

        pos_gen = gen.flow_from_directory(POS_DIR,
                                          target_size=(224, 224),
                                          batch_size=batch_size,
                                          color_mode='rgb')

        neg_gen = gen.flow_from_directory(NEG_DIR, 
                                          target_size=(224, 224),
                                          batch_size=batch_size,
                                          color_mode='rgb')
    
#         print("Anchor: {} , Neg: {}".format(anchor_label, neg_label))
        X1i = anchor_gen.next()
        X2i = pos_gen.next()
        X3i = neg_gen.next()
        
        yield [X1i[0], X2i[0], X3i[0]], X1i[1]
        
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
    
def train(model, gen = gen, epochs = 1000, steps = 100, batch_size = 4):
    train_generator = input_triplet_gen(gen, train_data_dir, num_classes, batch_size)
    val_generator = input_triplet_gen(gen, val_data_dir, num_classes, batch_size)
    
    my_callbacks = [
    EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=100),
    ModelCheckpoint(filepath='./trained/RESNET_UNFREEZE_0/{epoch:06d}-{loss:.4f}-{val_loss:.4f}.h5', save_best_only=True, monitor='val_loss', mode='min')
    ]
    
    model.fit(train_generator,
                  steps_per_epoch = steps, 
                  epochs=epochs, 
                  validation_data = val_generator,
                  validation_steps = 10,
                  use_multiprocessing=True,
                  callbacks = my_callbacks)
    
    
    
if __name__ == '__main__':
    args = parser.parse_args()
    
    batch_size = args.batch_size
    
    print('-------------------------------------------------------')
    print('Starting PROCESS 1: Creating model...')
    print('-------------------------------------------------------')
    
    base, model = create_res_model(args.resver)
    
    freeze_layer(base, int(346))   #freeze all
    
    model.compile(optimizer=Adam(learning_rate=0.0001, clipnorm=3.0),
                    loss=lossless_triplet_loss)
    
    print('-------------------------------------------------------')
    print('Starting PROCESS 2: Loading weights')
    print('-------------------------------------------------------')
    
    freeze_layer(base, int(args.previous_unfreeze))
    model.load_weights(args.weights_dir)
    print("Successfully loaded weights from {}".format(args.weights_dir))
    
    freeze_layer(base, int(args.current_unfreeze))
    
    print('-------------------------------------------------------')
    print('Starting PROCESS 3: Training model')
    print('-------------------------------------------------------')
    
    #create generator
    
    train_generator = input_triplet_gen(gen, train_data_dir, num_classes, batch_size)
    val_generator = input_triplet_gen(gen, val_data_dir, num_classes, batch_size)
    
    my_callbacks = [
    EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=100),
    ModelCheckpoint(filepath='./trained/RESNET101_UNFREEZE_11/{epoch:06d}-{loss:.4f}-{val_loss:.4f}.h5', save_best_only=True, monitor='val_loss', mode='min')
    ]

    # Training the model
    model.fit(train_generator,
                  steps_per_epoch = args.steps, 
                  epochs=args.epochs, 
                  validation_data = val_generator,
                  validation_steps = 10,
                  use_multiprocessing=True,
                  callbacks = my_callbacks)
