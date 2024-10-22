from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
import os
from detectron2.engine import DefaultPredictor
from PIL import Image
import cv2
import numpy as np



def model():
    cfg = get_cfg()
    cfg.merge_from_file('model/mask_rcnn_R_50_FPN_3x.yaml')
    cfg.DATASETS.TRAIN = ()
    cfg.DATASETS.TEST = () 
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.MODEL.WEIGHTS = "detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl" 
    cfg.SOLVER.IMS_PER_BATCH = 1
    cfg.SOLVER.BASE_LR = 0.001
    cfg.SOLVER.MAX_ITER = 100
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128 
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 13
    cfg.MODEL.WEIGHTS = os.path.join( "model/model_final_0.272_lr0.0001.pth")
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7 
    cfg.DATASETS.TEST = ("../Fashion-AI-segmentation/sample/", )
    predictor = DefaultPredictor(cfg)
    
    return predictor


def predict(img, savepath):
    im=cv2.imread(img)
    output=model()(im)
    mask=output['instances'].pred_masks.cpu().data.numpy()
    if mask.shape[0] != 0:
        base = np.zeros((mask.shape[1], mask.shape[2], 3))
        for m in range(mask.shape[0]):
            for i in range(3):
                for j in range(mask.shape[1]):
                    for k in range(mask.shape[2]):
                        if mask[m][j][k]==True:
                            base[j][k][i]=im[j][k][i]

    img_rgb=transparent_back(base)
    img_rgb.save(savepath[:-3]+'png')



def transparent_back(image):
    img=cv2.cvtColor(image.astype('uint8'),cv2.COLOR_BGR2RGB)
    image=Image.fromarray(img)
    image=image.convert('RGBA')
    L,H=image.size
    color_0=image.getpixel((0,0))
    for h in range(H):
        for l in range(L):
            dot=(l,h)
            color_1=image.getpixel(dot)
            if color_1==color_0:
                color_1=color_1[:-1]+(0,)
                image.putpixel(dot,color_1)
    return image    
    


def mask(start=0,time=100):
    print(f"starting from {int(start)+1}, to {int(start)+int(time)+1}")
    start=int(start)
    time=int(time)
    
    folder_index=start
    for i in fold_list[start:start+time]:
        listdir=os.listdir('mmfashion/'+i)
        if not os.path.exists('result/'+'('+str(folder_index+1)+')'+i):
            os.mkdir('result/'+'('+str(folder_index+1)+')'+i)
        print(str(folder_index+1)+' '+i)
        cnt=1
        for j in listdir:
            if cnt%10==0:
                print(str(cnt)+'/'+str(len(listdir)))
                print(i+j)
            predict('mmfashion/'+i+'/'+j,'result/'+'('+str(folder_index+1)+')'+i+'/'+j )
            cnt+=1
        folder_index+=1
     
  
        
def seoulmask(dir,start=0,time=1):
    img_list=os.listdir(dir)
    img_list=sorted(img_list)
    start=int(start)
    time=int(time)
    print(f"starting from {start}, to {start+time-1}")
    cnt=1
    if not os.path.exists(dir+'result'):
        os.mkdir(dir+'result')
    for i in img_list[start:start+time]:
        try:
            predict(dir+'/'+i, dir+'result/'+i)
            if cnt%10==0:
                print('***now converting*** : '+i+'  ****  '+str(cnt)+'/'+str(time))
        except:
            print('****error****     ',i,'    ***',str(cnt)+'/'+str(time))
        cnt+=1
        
if __name__=="__main__":
    import argparse
    
    parser=argparse.ArgumentParser(
        description='Remove Background')
    parser.add_argument("--shop", help='store', default='seoul')
    parser.add_argument("--dir",
                         help="ImageDirectory")
    parser.add_argument("--start",
                        help="startNum")
    parser.add_argument("--time",
                        help="times")
    args=parser.parse_args()
    if args.shop=='mmfashion':
        fold_list=os.listdir('mmfashion')
        fold_list=sorted(fold_list)[1:]

        mask(args.start, args.time)
        
    else:
        seoulmask(args.dir,args.start,args.time)
