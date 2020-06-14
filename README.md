# Personal_Shopper-KJH-KIDS-
<img src='./siyeon.gif'>



## Introduction

<a href='15.164.247.135:8080'> oddeye</a> 👀 is a personalized style assistance service powered by deep learning AI technology. Some of the main functions oddeye offers are

- item recommendation based on style icons of your liking (similarity)
  - e.g. IU, Jennie of BlackPink, ...
- item recommendation based on items of your liking (similarity)
- (tbd) item recommendation based on items that you already own (compatibility)

oddeye's goal is for our users to be able to receive personalized fashion recommendtaion and ultimately build your own unique style and taste in fashion. It will almost be like having a personal shopper! (hence our team name: personal shopper 😝)

Our technology is based on triplet network and object segmentation. Triplet network is trained on 298k fashion images classified into 5620 classes(<a href='https://github.com/open-mmlab/mmfashion'> mmfashion dataset </a>) to determine similarity between styles and items. Object segmentation is used for image preprocessing so that the triplet network have less trouble throughout the training process. Our segmentaiton is powered by <a href='https://github.com/facebookresearch/detectron2'>Facebook's detectron2</a>. You can learn more about each of the technology down below!

## Triplet Network 👭

[Triplet README](./model/)



## Segmentation ✂️

[Segmentation_README](./model/seg/)